#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "index.json"
SOURCES = ROOT / "sources"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COUNTRY = re.compile(r"^[A-Z]{2}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_CATEGORIES = {
    "general", "sports", "movies", "kids", "news", "music",
    "documentary", "lifestyle", "regional", "series", "other"
}
ALLOWED_EXTENSIONS = {".svg", ".png", ".webp"}
ALLOWED_STATUS = {"active", "legacy", "deprecated"}
REQUIRED_FIELDS = {
    "id", "name", "country", "category", "file", "aliases", "status",
    "sha256", "license", "sourcePage", "trademarked", "sourceManifest",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    if not INDEX.is_file():
        fail("data/index.json is missing")

    data = json.loads(INDEX.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1:
        fail("schemaVersion must be 1")

    channels = data.get("channels")
    if not isinstance(channels, list):
        fail("channels must be an array")

    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    seen_aliases: dict[tuple[str, str], str] = {}

    for channel in channels:
        if not isinstance(channel, dict):
            fail("every channel entry must be an object")

        missing = sorted(REQUIRED_FIELDS - set(channel))
        if missing:
            fail(f"channel missing required fields: {', '.join(missing)}")

        cid = channel.get("id", "")
        if not isinstance(cid, str) or not SLUG.fullmatch(cid):
            fail(f"invalid id: {cid}")
        if cid in seen_ids:
            fail(f"duplicate id: {cid}")
        seen_ids.add(cid)

        name = channel.get("name")
        if not isinstance(name, str) or not name.strip():
            fail(f"invalid name for {cid}")

        country = channel.get("country", "")
        if not isinstance(country, str) or not COUNTRY.fullmatch(country):
            fail(f"invalid country for {cid}: {country}")

        category = channel.get("category")
        if category not in ALLOWED_CATEGORIES:
            fail(f"invalid category for {cid}: {category}")

        status = channel.get("status")
        if status not in ALLOWED_STATUS:
            fail(f"invalid status for {cid}: {status}")

        rel = channel.get("file", "")
        if not isinstance(rel, str) or not rel:
            fail(f"invalid file path for {cid}")
        if rel in seen_files:
            fail(f"duplicate file mapping: {rel}")
        seen_files.add(rel)

        rel_path = Path(rel)
        if ".." in rel_path.parts or rel_path.is_absolute():
            fail(f"unsafe path for {cid}: {rel}")
        if rel_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            fail(f"unsupported extension for {cid}: {rel_path.suffix}")
        if len(rel_path.parts) < 3 or rel_path.parts[0] != "countries" or rel_path.parts[1] != country.lower():
            fail(f"file for {cid} must be under countries/{country.lower()}/")

        asset = ROOT / rel_path
        if not asset.is_file():
            fail(f"missing asset for {cid}: {rel}")

        expected_sha = channel.get("sha256")
        if not isinstance(expected_sha, str) or not SHA256.fullmatch(expected_sha):
            fail(f"invalid sha256 for {cid}: {expected_sha}")
        actual_sha = file_sha256(asset)
        if actual_sha != expected_sha:
            fail(f"sha256 mismatch for {cid}: expected {expected_sha}, got {actual_sha}")

        license_text = channel.get("license")
        if not isinstance(license_text, str) or not license_text.strip():
            fail(f"missing license text for {cid}")

        source_page = channel.get("sourcePage")
        if not isinstance(source_page, str) or not source_page.startswith("https://"):
            fail(f"invalid sourcePage for {cid}")

        trademarked = channel.get("trademarked")
        if not isinstance(trademarked, bool):
            fail(f"trademarked must be boolean for {cid}")

        source_manifest = channel.get("sourceManifest")
        if not isinstance(source_manifest, str) or not source_manifest.endswith(".json"):
            fail(f"invalid sourceManifest for {cid}: {source_manifest}")
        if Path(source_manifest).name != source_manifest:
            fail(f"unsafe sourceManifest for {cid}: {source_manifest}")
        if not (SOURCES / source_manifest).is_file():
            fail(f"sourceManifest does not exist for {cid}: {source_manifest}")

        aliases = channel.get("aliases")
        if not isinstance(aliases, list) or not all(isinstance(a, str) and a.strip() for a in aliases):
            fail(f"aliases must be a non-empty-string array for {cid}")
        folded = [a.casefold().strip() for a in aliases]
        if len(folded) != len(set(folded)):
            fail(f"duplicate aliases for {cid}")
        for alias in folded:
            key = (country, alias)
            owner = seen_aliases.get(key)
            if owner and owner != cid:
                fail(f"alias collision in {country}: {alias!r} belongs to both {owner} and {cid}")
            seen_aliases[key] = cid

    print(f"OK: {len(seen_ids)} indexed picons validated with hashes, provenance and schema invariants")


if __name__ == "__main__":
    main()
