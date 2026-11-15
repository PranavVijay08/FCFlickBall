"""Retrieve version-pinned, licensed EXTERNAL match data with checksum verification."""
import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

CATALOGUE = "https://api.figshare.com/v2/articles/28196177/versions/1"
SPLITS = {"train": ["J03WMX", "J03WN1", "J03WOH", "J03WOY"],
          "validation": ["J03WPY", "J03WQQ"], "test": ["J03WR9"]}


def digest(path, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def download(dest, metadata_only=False):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(CATALOGUE, timeout=60) as response:
        catalogue = json.load(response)
    (dest / "catalogue-v1.json").write_text(json.dumps(catalogue, indent=2), encoding="utf-8")
    records = []
    for entry in catalogue["files"]:
        name = entry["name"]
        if not ("matchinformation" in name or (not metadata_only and "positions_raw" in name)):
            continue
        path = dest / name
        expected = entry["computed_md5"]
        if not (path.exists() and path.stat().st_size == entry["size"] and digest(path, "md5") == expected):
            print("Downloading external", name, entry["size"], "bytes", flush=True)
            partial = path.with_suffix(".partial")
            with urllib.request.urlopen(entry["download_url"], timeout=120) as response, partial.open("wb") as f:
                for block in iter(lambda: response.read(1024 * 1024), b""):
                    f.write(block)
            if partial.stat().st_size != entry["size"] or digest(partial, "md5") != expected:
                raise ValueError("External download checksum/size mismatch: " + name)
            partial.replace(path)
        records.append({"name": name, "url": entry["download_url"], "size": entry["size"],
                        "md5": expected, "sha256": digest(path)})
        print("Verified external", name, flush=True)
    manifest = {"dataset": "IDSSE", "version": 1, "catalogue": CATALOGUE,
                "license": catalogue["license"], "splits": SPLITS, "files": records}
    (dest / "download_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", default="external_data/idsse")
    parser.add_argument("--metadata-only", action="store_true")
    args = parser.parse_args()
    download(args.dest, args.metadata_only)
