#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COUNTRY = re.compile(r"^[A-Z]{2}$")
ALLOWED_CATEGORIES = {
    "general", "sports", "movies", "kids", "news", "music",
    "documentary", "lifestyle", "regional", "series", "other"
}
ALLOWED_HOSTS = {"commons.wikimedia.org", "upload.wikimedia.org"}
ALLOWED_EXTENSIONS = {".svg", ".png", ".webp"}
REQUIRED = {"id", "name", "country", "category", "path", "url", "license", "sourcePage"}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    files = sorted(SOURCES.glob("*.json"))
    if not files:
        fail("no source manifests found")

    seen_ids: dict[str, str] = {}
    seen_paths: dict[str, str] = {}
    seen_aliases: dict[tuple[str, str], str] = {}
    total = 0

    for manifest in files:
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"{manifest.name}: invalid JSON: {exc}")

        declared_country = payload.get("country")
        if not COUNTRY.fullmatch(str(declared_country or "")):
            fail(f"{manifest.name}: invalid top-level country: {declared_country}")

        channels = payload.get("channels")
        if not isinstance(channels, list) or not channels:
            fail(f"{manifest.name}: channels must be a non-empty array")

        for item in channels:
            total += 1
            missing = sorted(REQUIRED - set(item))
            if missing:
                fail(f"{manifest.name}: {item.get('id', '?')} missing fields: {', '.join(missing)}")

            cid = str(item["id"])
            if not SLUG.fullmatch(cid):
                fail(f"{manifest.name}: invalid id: {cid}")
            if cid in seen_ids:
                fail(f"duplicate id {cid}: {seen_ids[cid]} and {manifest.name}")
            seen_ids[cid] = manifest.name

            country = str(item["country"])
            if country != declared_country:
                fail(f"{manifest.name}: {cid} country {country} != manifest country {declared_country}")

            category = item["category"]
            if category not in ALLOWED_CATEGORIES:
                fail(f"{manifest.name}: {cid} invalid category: {category}")

            rel = Path(str(item["path"]))
            if rel.is_absolute() or ".." in rel.parts:
                fail(f"{manifest.name}: {cid} unsafe path: {rel}")
            if rel.suffix.lower() not in ALLOWED_EXTENSIONS:
                fail(f"{manifest.name}: {cid} unsupported extension: {rel.suffix}")
            if len(rel.parts) < 3 or rel.parts[0] != "countries" or rel.parts[1] != country.lower():
                fail(f"{manifest.name}: {cid} path must be under countries/{country.lower()}/")
            rel_text = rel.as_posix()
            if rel_text in seen_paths:
                fail(f"duplicate output path {rel_text}: {seen_paths[rel_text]} and {manifest.name}")
            seen_paths[rel_text] = manifest.name

            for field in ("url", "sourcePage"):
                parsed = urllib.parse.urlparse(str(item[field]))
                if parsed.scheme != "https":
                    fail(f"{manifest.name}: {cid} {field} must use https")
                if parsed.hostname not in ALLOWED_HOSTS:
                    fail(f"{manifest.name}: {cid} {field} host not allowed: {parsed.hostname}")

            aliases = item.get("aliases", [])
            if not isinstance(aliases, list):
                fail(f"{manifest.name}: {cid} aliases must be an array")
            if len(aliases) != len(set(aliases)):
                fail(f"{manifest.name}: {cid} contains duplicate aliases")
            for alias in aliases:
                key = (country, str(alias).casefold().strip())
                owner = seen_aliases.get(key)
                if owner and owner != cid:
                    fail(f"alias collision in {country}: {alias!r} belongs to both {owner} and {cid}")
                seen_aliases[key] = cid

    print(f"OK: {len(files)} manifests, {total} channel definitions validated")


if __name__ == "__main__":
    main()
