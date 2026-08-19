#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "index.json"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COUNTRY = re.compile(r"^[A-Z]{2}$")
ALLOWED_CATEGORIES = {
    "general", "sports", "movies", "kids", "news", "music",
    "documentary", "lifestyle", "regional", "other"
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1:
        fail("schemaVersion must be 1")

    seen_ids = set()
    seen_files = set()

    for channel in data.get("channels", []):
        cid = channel.get("id", "")
        if not SLUG.fullmatch(cid):
            fail(f"invalid id: {cid}")
        if cid in seen_ids:
            fail(f"duplicate id: {cid}")
        seen_ids.add(cid)

        country = channel.get("country", "")
        if not COUNTRY.fullmatch(country):
            fail(f"invalid country for {cid}: {country}")

        category = channel.get("category")
        if category not in ALLOWED_CATEGORIES:
            fail(f"invalid category for {cid}: {category}")

        rel = channel.get("file", "")
        if rel in seen_files:
            fail(f"duplicate file mapping: {rel}")
        seen_files.add(rel)

        if ".." in Path(rel).parts or Path(rel).is_absolute():
            fail(f"unsafe path for {cid}: {rel}")

        asset = ROOT / rel
        if not asset.is_file():
            fail(f"missing asset for {cid}: {rel}")

        aliases = channel.get("aliases", [])
        if len(aliases) != len(set(aliases)):
            fail(f"duplicate aliases for {cid}")

    print(f"OK: {len(seen_ids)} indexed picons validated")


if __name__ == "__main__":
    main()
