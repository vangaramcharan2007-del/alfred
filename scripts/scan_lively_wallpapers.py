import json
from pathlib import Path

lively_pkg = Path(r"C:\Users\vanga\AppData\Local\Packages\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy\LocalCache\Local\Lively Wallpaper")
print("Scanning Lively wallpapers in:", lively_pkg)

found = []
for p in lively_pkg.rglob("LivelyInfo.json"):
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        title = data.get("Title", "Untitled")
        fn = data.get("FileName", "")
        thumb = data.get("Thumbnail", "")
        thumb_p = p.parent / thumb if thumb else None
        thumb_exists = thumb_p.exists() if thumb_p else False
        found.append({
            "title": title,
            "filename": fn,
            "folder": p.parent.name,
            "folder_path": str(p.parent),
            "thumb": str(thumb_p) if thumb_exists else None,
            "thumb_exists": thumb_exists,
            "info_path": str(p)
        })
    except Exception:
        pass

print(f"Total wallpapers found: {len(found)}")
for i, item in enumerate(found, 1):
    print(f"{i:2d}. {item['title']} | File: {item['filename']} | Thumb: {item['thumb_exists']}")
