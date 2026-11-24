#!/usr/bin/env python3
"""
Rizk photo downloader
Downloads the individually listed Wikimedia Commons images into assets/recipes/.
Only accepts CC0, Public Domain, CC BY, or CC BY-SA licenses and writes attribution
details to PHOTO-CREDITS.md. Run from the Rizk project folder:
    python download-assets.py
Requires: Python 3.9+ and requests (python -m pip install requests)
"""
import json, re, time
from pathlib import Path
from urllib.parse import quote
import requests

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "assets" / "recipes"
DEST.mkdir(parents=True, exist_ok=True)
SOURCES = json.loads((ROOT / "photo-sources.json").read_text(encoding="utf-8"))
API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "RizkRecipeApp/1.0 (photo attribution and license verification)"}
ALLOWED = ("cc0", "public domain", "cc by", "cc-by", "cc by-sa", "cc-by-sa")

def clean(s):
    return re.sub(r"<[^>]+>", "", str(s or "")).strip()

credits = [
    "# Rizk — Photo credits",
    "",
    "Photos are downloaded from Wikimedia Commons. Each entry below is checked against the file's current Commons metadata.",
    "Please keep this file with the app when redistributing it.",
    ""
]
ok, skipped = 0, []

for item in SOURCES:
    title = "File:" + item["file"]
    params = {
        "action": "query", "format": "json", "prop": "imageinfo",
        "iiprop": "url|extmetadata", "titles": title
    }
    try:
        data = requests.get(API, params=params, headers=HEADERS, timeout=30).json()
        page = next(iter(data["query"]["pages"].values()))
        if "imageinfo" not in page:
            skipped.append((item["dish"], "Commons file not found"))
            continue
        info = page["imageinfo"][0]
        meta = info.get("extmetadata", {})
        artist = clean(meta.get("Artist", {}).get("value", "Author not stated"))
        license_name = clean(meta.get("LicenseShortName", {}).get("value", ""))
        license_url = clean(meta.get("LicenseUrl", {}).get("value", ""))
        usage = (license_name + " " + license_url).lower()
        if not any(term in usage for term in ALLOWED):
            skipped.append((item["dish"], f"License not in automatic allow-list: {license_name or 'unknown'}"))
            continue
        url = info["url"]
        ext = Path(url.split("?")[0]).suffix.lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp"):
            ext = ".jpg"
        filename = item["slug"] + ext
        r = requests.get(url, headers=HEADERS, timeout=60)
        r.raise_for_status()
        (DEST / filename).write_bytes(r.content)
        page_url = "https://commons.wikimedia.org/wiki/" + quote(title.replace(" ", "_"), safe=":/()'")
        credits += [
            f"## {item['dish']}",
            f"- File: [{item['file']}]({page_url})",
            f"- Author: {artist}",
            f"- License: {license_name} — {license_url}",
            f"- Local file: `assets/recipes/{filename}`",
            ""
        ]
        print("Downloaded:", item["dish"], "->", filename, "|", license_name)
        ok += 1
        time.sleep(0.25)
    except Exception as e:
        skipped.append((item["dish"], str(e)))

if skipped:
    credits += ["## Not downloaded", ""]
    for dish, why in skipped:
        credits.append(f"- **{dish}:** {why}")
    credits.append("")
(ROOT / "PHOTO-CREDITS.md").write_text("\n".join(credits), encoding="utf-8")
print(f"\nFinished: {ok} photos downloaded; {len(skipped)} skipped.")
print("See PHOTO-CREDITS.md for attribution and any skipped sources.")
