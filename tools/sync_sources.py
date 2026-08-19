#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
INDEX = ROOT / "data" / "index.json"
ATTR = ROOT / "ATTRIBUTION.md"
ALLOWED_HOSTS = {
    "commons.wikimedia.org",
    "upload.wikimedia.org",
}
MAX_BYTES = 5 * 1024 * 1024


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "X1-Picons-Sync/1.0 (+https://github.com/x1-dotcom/picons)"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        final_host = urllib.parse.urlparse(response.geturl()).hostname or ""
        if final_host not in ALLOWED_HOSTS:
            raise RuntimeError(f"Unexpected redirect host: {final_host}")
        data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise RuntimeError("Asset exceeds 5 MiB limit")
        return data


def load_sources():
    entries = []
    for file in sorted(SOURCES.glob("*.json")):
        payload = json.loads(file.read_text(encoding="utf-8"))
        for item in payload.get("channels", []):
            item = dict(item)
            item["_source_manifest"] = file.name
            entries.append(item)
    return entries


def main() -> None:
    channels = []
    attribution = [
        "# X1 Picons — Attribution & Source Register",
        "",
        "Generated automatically from `sources/*.json`.",
        "",
        "Channel names/logos may remain protected trademarks even when the file is freely reusable.",
        "",
    ]

    for item in load_sources():
        required = ["id", "name", "country", "category", "path", "url", "license", "sourcePage"]
        missing = [key for key in required if not item.get(key)]
        if missing:
            raise RuntimeError(f"{item.get('id','?')}: missing {', '.join(missing)}")

        host = urllib.parse.urlparse(item["url"]).hostname or ""
        if host not in ALLOWED_HOSTS:
            raise RuntimeError(f"{item['id']}: source host not allowed: {host}")

        out = ROOT / item["path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        data = fetch(item["url"])

        suffix = out.suffix.lower()
        if suffix == ".svg" and b"<svg" not in data[:2048].lower():
            raise RuntimeError(f"{item['id']}: expected SVG payload")
        if suffix == ".png" and not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError(f"{item['id']}: expected PNG payload")

        out.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()

        channels.append({
            "id": item["id"],
            "name": item["name"],
            "country": item["country"],
            "category": item["category"],
            "file": item["path"],
            "aliases": item.get("aliases", []),
            "sha256": digest,
            "license": item["license"],
            "sourcePage": item["sourcePage"],
            "trademarked": bool(item.get("trademarked", True)),
            "sourceManifest": item["_source_manifest"],
        })

        attribution.extend([
            f"## {item['name']} ({item['country']})",
            f"- File: `{item['path']}`",
            f"- Source page: {item['sourcePage']}",
            f"- License/status: {item['license']}",
            f"- Trademark notice: {'yes' if item.get('trademarked', True) else 'no/unknown'}",
            "",
        ])

    INDEX.write_text(
        json.dumps({
            "schemaVersion": 1,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "channels": channels,
        }, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    ATTR.write_text("\n".join(attribution), encoding="utf-8")
    print(f"Synced {len(channels)} picons")


if __name__ == "__main__":
    import urllib.parse
    main()
