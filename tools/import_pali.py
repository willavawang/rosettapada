"""Fetch newly authorized chapter files from the already pinned Bilara revision.

Existing frozen files are verified, never refreshed. No upstream revision changes.
"""
from pathlib import Path
from urllib.request import urlopen, Request
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
manifest_path = ROOT / "data/chapters.json"
manifest = json.loads(manifest_path.read_text())
known = {entry["local"]: entry for entry in manifest["files"]}
revision = manifest["upstream"]["commit"]
templates = [
    ("root-pli-ms", "root/pli/ms/sutta/kn/dhp"),
    ("translation-en-sujato", "translation/en/sujato/sutta/kn/dhp"),
    ("html", "html/pli/ms/sutta/kn/dhp"),
]
added = []
for chapter in manifest["chapters"]:
    for suffix, directory in templates:
        filename = f'{chapter["uid"]}_{suffix}.json'
        local = f"data/pali/{filename}"
        path = ROOT / local
        if local in known:
            assert hashlib.sha256(path.read_bytes()).hexdigest() == known[local]["sha256"], f"Frozen file changed: {local}"
            continue
        upstream = f"{directory}/{filename}"
        url = f"https://raw.githubusercontent.com/suttacentral/bilara-data/{revision}/{upstream}"
        with urlopen(Request(url, headers={"User-Agent": "Rosettapada source verification"}), timeout=30) as response:
            content = response.read()
        parsed = json.loads(content)
        assert isinstance(parsed, dict) and parsed, f"Empty source: {url}"
        path.write_bytes(content)
        entry = {
            "local": local,
            "upstream_path": upstream,
            "git_blob": hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest(),
            "sha256": hashlib.sha256(content).hexdigest(),
        }
        manifest["files"].append(entry)
        added.append(local)
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
print(f"Pinned revision {revision}; verified {len(known)} existing files and added {len(added)} chapter files.")
