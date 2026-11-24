# Rizk — Bangladeshi recipe app

A responsive, single-page recipe app with Home, Search, and Watch Later pages, bilingual English/Bangla recipe instructions, local saved recipes, category filters, and a language setting on Watch Later.

## Start
Open `index.html` in a modern browser. For the local image files to appear, first download the photo assets:

```bash
python -m pip install requests
python download-assets.py
```

Then keep the `assets/recipes/` folder beside `index.html`. The app uses relative local image paths and does not hotlink photos at runtime.

## Photo status
The ZIP includes a source manifest and a downloader, not the binary image files. The execution environment used to prepare this project cannot fetch binary image files from Wikimedia Commons, so I have not claimed those photos are already bundled. The downloader queries each Commons file's live metadata, checks the license against an allow-list, downloads it, and creates `PHOTO-CREDITS.md`. Any unverified or incompatible file is skipped and listed in that report.

## Structure
- `index.html` — app
- `photo-sources.json` — individually named Commons photo sources
- `download-assets.py` — license-checking photo downloader
- `assets/recipes/` — destination folder for downloaded local photos
