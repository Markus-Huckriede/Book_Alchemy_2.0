# Book Alchemy

Book Alchemy ist eine kleine, installierbare Bibliotheks-App mit Flask. Bücher können per ISBN oder Titel hinzugefügt werden; die Metadaten werden kostenlos über Open Library gesucht. Autorinnen und Autoren werden automatisch angelegt und bleiben durchsuchbar.

## Funktionen

- Bücher per ISBN oder Titel hinzufügen
- Automatische Suche nach Titel, Autor, Erscheinungsjahr, ISBN und Cover über Open Library
- Automatisches Anlegen von Autorinnen und Autoren
- Suche und Sortierung nach Titel oder Autor
- Detailseiten für Bücher und Autoren
- Kostenloser ISBN-Scanner im Browser, sofern `BarcodeDetector` unterstützt wird
- Installierbar als PWA auf Smartphone und Desktop

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Starten

```bash
python app.py
```

Die App läuft standardmäßig auf:

```text
http://127.0.0.1:5002
```

Du kannst den Port überschreiben:

```bash
PORT=5003 python app.py
```

## Deployment auf Vercel

Dieses Repo ist für Vercel vorbereitet:

- `app.py` exportiert die Flask-Instanz `app`, die Vercel als Function deployt.
- `vercel.json` routet alle Requests auf `app.py` und nimmt `templates/` sowie `static/` ins Function-Bundle auf.
- `public/` enthält eine Kopie der statischen Assets, damit Vercel sie direkt ausliefern kann.
- `.vercelignore` hält lokale Dateien wie `.venv/`, `library.sqlite` und Python-Caches aus dem Deployment heraus.

Deployment per Vercel CLI:

```bash
npm i -g vercel
vercel login
vercel
vercel --prod
```

Alternativ kannst du das Git-Repository in Vercel importieren. Als Framework Preset reicht `Other`; ein Build Command ist nicht nötig.

Lege in Vercel unter `Project Settings` -> `Environment Variables` diese Variablen an:

```text
SECRET_KEY=ein-langer-zufaelliger-string
DATABASE_URL=postgresql://...
```

Wenn du Vercel Postgres/Storage verwendest, kann die Variable auch `POSTGRES_URL` heißen; die App liest beide Namen. Trage bei `DATABASE_URL` niemals den Platzhalter `postgresql://...` ein, sondern immer den vollständigen Connection String deiner Datenbank.

Einen Secret Key kannst du lokal so erzeugen:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Wichtig: `SECRET_KEY` ist auf Vercel erforderlich. Ohne `DATABASE_URL` nutzt die App dort SQLite im flüchtigen `/tmp`-Verzeichnis, was nur für einen Test-Deploy gedacht ist. Für produktive Nutzung solltest du eine Postgres-Datenbank anbinden und deren Connection String als `DATABASE_URL` in Vercel setzen.

## Nutzung

Öffne `Buch hinzufügen`, gib eine ISBN oder einen Titel ein und speichere das gefundene Buch. Wenn Open Library passende Daten findet, werden Buch und Autor automatisch in der lokalen SQLite-Datenbank gespeichert.

Der ISBN-Scanner nutzt die Kamera deines Geräts. Falls dein Browser die Barcode-Erkennung nicht unterstützt, kannst du die ISBN manuell eingeben.

## PWA installieren

Die App enthält ein Web App Manifest, Icons und einen Service Worker. Im Browser kann sie über die Installationsfunktion als App hinzugefügt werden. Für echte Geräte und produktive Nutzung sollte die App über HTTPS bereitgestellt werden; `localhost` funktioniert in der Entwicklung.

## Projektstruktur

```text
app.py                 Flask-App-Factory und Startpunkt
routes.py              Routen und View-Logik
book_lookup.py         Open-Library-Abfragen
data_models.py         SQLAlchemy-Modelle
templates/             HTML-Templates
static/                CSS, JavaScript, PWA-Dateien und Icons
requirements.txt       Python-Abhängigkeiten
```

## Hinweise

Die lokale Datei `library.sqlite` enthält deine gespeicherten Bücher und ist bewusst nicht im Git-Repository enthalten. Ebenso werden `.venv/` und Python-Cache-Dateien ignoriert.

---

# Book Alchemy

Book Alchemy is a small installable library app built with Flask. Books can be added by ISBN or title; metadata is fetched for free from Open Library. Authors are created automatically and remain searchable.

## Features

- Add books by ISBN or title
- Automatically fetch title, author, publication year, ISBN, and cover from Open Library
- Automatically create authors
- Search and sort by title or author
- Detail pages for books and authors
- Free in-browser ISBN scanner when `BarcodeDetector` is supported
- Installable as a PWA on mobile and desktop

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

By default, the app runs at:

```text
http://127.0.0.1:5002
```

You can override the port:

```bash
PORT=5003 python app.py
```

## Deploy to Vercel

This repo is prepared for Vercel:

- `app.py` exports the Flask instance `app`, which Vercel deploys as a Function.
- `vercel.json` routes all requests to `app.py` and includes `templates/` plus `static/` in the Function bundle.
- `public/` contains a copy of the static assets so Vercel can serve them directly.
- `.vercelignore` keeps local files such as `.venv/`, `library.sqlite`, and Python caches out of the deployment.

Deploy with the Vercel CLI:

```bash
npm i -g vercel
vercel login
vercel
vercel --prod
```

You can also import the Git repository in Vercel. Use `Other` as the Framework Preset; no Build Command is needed.

Add these variables in Vercel under `Project Settings` -> `Environment Variables`:

```text
SECRET_KEY=a-long-random-string
DATABASE_URL=postgresql://...
```

If you use Vercel Postgres/Storage, the variable may also be named `POSTGRES_URL`; the app reads both names. Never set `DATABASE_URL` to the placeholder `postgresql://...`; use the full connection string from your database provider.

You can generate a secret key locally with:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Important: `SECRET_KEY` is required on Vercel. Without `DATABASE_URL`, the app uses SQLite in ephemeral `/tmp` storage, which is only meant for a test deployment. For production use, connect a Postgres database and set its connection string as `DATABASE_URL` in Vercel.

## Usage

Open `Buch hinzufügen`, enter an ISBN or a title, and save the found book. If Open Library returns matching metadata, the book and author are stored automatically in the local SQLite database.

The ISBN scanner uses your device camera. If your browser does not support barcode detection, you can enter the ISBN manually.

## PWA Installation

The app includes a web app manifest, icons, and a service worker. It can be installed through the browser's install option. For real devices and production use, serve the app over HTTPS; `localhost` works during development.

## Project Structure

```text
app.py                 Flask app factory and entry point
routes.py              Routes and view logic
book_lookup.py         Open Library lookup logic
data_models.py         SQLAlchemy models
templates/             HTML templates
static/                CSS, JavaScript, PWA files, and icons
requirements.txt       Python dependencies
```

## Notes

The local `library.sqlite` file contains your saved books and is intentionally not committed to Git. The `.venv/` folder and Python cache files are ignored as well.
