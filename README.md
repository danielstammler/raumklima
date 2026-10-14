# Raumklima & Heizung

Website zu den Loxone-Klimadaten im Google Sheet „loxone_climate“: Ist- und Solltemperaturen
aller Räume als Hausschnitt, Verlauf je Raum, Heatmaps für Soll-Abweichung, Luftfeuchte und
Ventilöffnung. Funktioniert auf Handy und PC, hell und dunkel.

## Dateien

| Datei | Zweck |
|---|---|
| `src/page.html` | Quelltext der Seite (HTML, CSS, JavaScript) |
| `build.py` | baut daraus die fertigen Seiten |
| `docs/index.html` | **die Live-Website** (von GitHub Pages ausgeliefert): lädt die Daten bei jedem Aufruf direkt aus dem Google Sheet und prüft alle 5 Minuten auf neue Werte |
| `dist/artifact.html` | Variante mit eingebettetem Datenstand (für das claude.ai-Artifact, dort sind externe Abrufe gesperrt) |

## Neu bauen

```bash
python3 build.py              # docs/index.html
python3 build.py --snapshot   # dist/artifact.html mit aktuellem Datenstand
```

## Öffentlich bereitstellen

`docs/index.html` ist eine einzelne statische Datei ohne Server-Logik. Sie läuft über GitHub Pages (Branch `main`, Ordner `/docs`); jeder andere statische Hoster genügt ebenso:

- **Netlify Drop**: den Ordner `docs` auf <https://app.netlify.com/drop> ziehen.
- **Cloudflare Pages**, **Vercel** o. ä. funktionieren genauso.

Voraussetzung: Das Google Sheet bleibt unter *Freigeben → Allgemeiner Zugriff* auf
„Jeder mit dem Link – Betrachter“ gestellt. Sonst zeigt die Seite einen Hinweis statt der Daten.

Die Seite setzt `noindex`, damit Suchmaschinen sie nicht aufnehmen. Wer den Link kennt, kann sie
und das Sheet trotzdem lesen.

## Annahmen

- „Im Soll“ = Ist-Temperatur höchstens 0,5 K vom Sollwert entfernt.
- Modus-Bezeichnungen kommen aus dem Tab `codebook`, Raum- und Stellantriebsnamen aus `controllers` und `actuators`.
- Zeiträume ab 7 Tagen laden ältere Werte stündlich (die letzten 24 Std weiterhin alle 10 Min), damit die Seite auch bei großen Datenmengen schnell bleibt.
- Spaltenpositionen werden beim Laden gegen die Kopfzeile geprüft. Verschiebt sich das Schema, lädt die Seite die Tabelle vollständig und sucht die Spalten über ihre Namen.
