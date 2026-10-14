#!/usr/bin/env python3
"""Baut die Raumklima-Website aus src/page.html.

  python3 build.py              docs/index.html    – lädt die Daten live aus dem Google Sheet (GitHub Pages)
  python3 build.py --snapshot   dist/artifact.html – mit eingebettetem Datenstand (für das claude.ai-Artifact)
"""
import argparse
import datetime
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
SHEET_ID = '1PRRNewgk2MVyh_9-VGFao4YBhNLhzdvUvgcVphER0yg'

# Gleiche Spaltenauswahl wie SPEC in src/page.html
TABLES = {
    'temperatures': (10000, 'select B,E,F,G,H,I order by B'),
    'humidity': (10001, 'select B,E,F,G order by B'),
    'valves': (10002, 'select B,E,G,H order by B'),
    'outdoor': (10003, 'select B,D,F order by B'),
    'controllers': (10005, 'select A,B,C,D'),
    'actuators': (10006, 'select A,B,C,D,E'),
    'codebook': (10007, 'select A,B,C,D'),
    'sync_status': (10010, 'select A,B'),
}

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Cpath d='M3 15 16 4l13 11v13H3z' fill='%2311151a'/%3E"
           "%3Crect x='13' y='16' width='6' height='12' rx='1' fill='%23eb6834'/%3E%3C/svg%3E")

WEB_HEAD = f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="Live-Ansicht der Loxone-Klimadaten: Ist- und Solltemperaturen, Luftfeuchte und Ventilöffnungen aller Räume.">
<meta name="theme-color" content="#f1f3f5" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0c0f12" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{FAVICON}">
<style>html{{-webkit-text-size-adjust:100%;text-size-adjust:100%}}:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}</style>
'''


def fetch(gid, tq):
    url = (f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&headers=1'
           f'&gid={gid}&tq={urllib.parse.quote(tq)}')
    with urllib.request.urlopen(url, timeout=60) as res:
        ctype = res.headers.get('content-type', '')
        body = res.read().decode('utf-8')
    if 'csv' not in ctype:
        raise SystemExit(f'gid {gid}: keine CSV-Antwort ({ctype}). Ist das Sheet noch öffentlich freigegeben?')
    return body


def build(snapshot):
    page = (ROOT / 'src' / 'page.html').read_text(encoding='utf-8')
    if snapshot:
        data = {
            'generated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'tables': {name: fetch(gid, tq) for name, (gid, tq) in TABLES.items()},
        }
        blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
        page = page.replace('<!--@@SNAPSHOT@@-->', f'<script type="application/json" id="rk-snapshot">{blob}</script>')
        page = page.replace('/*@@CONFIG@@*/', 'window.RK_CONFIG = {"mode": "snapshot"};')
        out = ROOT / 'dist' / 'artifact.html'
        rows = {k: v.count('\n') for k, v in data['tables'].items()}
        print('Datenstand eingebettet:', ', '.join(f'{k} {n}' for k, n in rows.items()))
    else:
        page = page.replace('<!--@@SNAPSHOT@@-->', '')
        page = page.replace('/*@@CONFIG@@*/', 'window.RK_CONFIG = {"mode": "live"};')
        cut = page.index('</style>') + len('</style>')
        page = WEB_HEAD + page[:cut] + '\n</head>\n<body>\n' + page[cut:].lstrip('\n') + '</body>\n</html>\n'
        out = ROOT / 'docs' / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding='utf-8')
    print(f'{out.relative_to(ROOT)}: {out.stat().st_size / 1024:.0f} KB')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--snapshot', action='store_true', help='Datenstand einbetten (für das Artifact)')
    build(ap.parse_args().snapshot)
