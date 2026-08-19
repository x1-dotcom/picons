#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
INDEX = ROOT / "data" / "index.json"
REPORT = ROOT / "data" / "sync-report.json"
ATTR = ROOT / "ATTRIBUTION.md"
ALLOWED_HOSTS = {
    "commons.wikimedia.org",
    "upload.wikimedia.org",
}
MAX_BYTES = 5 * 1024 * 1024
MAX_ATTEMPTS = 3


def fetch(url: str) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "X1-Picons-Sync/2.2 (+https://github.com/x1-dotcom/picons)",
                    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                },
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                final_host = urllib.parse.urlparse(response.geturl()).hostname or ""
                if final_host not in ALLOWED_HOSTS:
                    raise RuntimeError(f"Unexpected redirect host: {final_host}")
                data = response.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    raise RuntimeError("Asset exceeds 5 MiB limit")
                return data
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, RuntimeError) as exc:
            last_error = exc
            if attempt < MAX_ATTEMPTS:
                time.sleep(attempt * 2)
    raise RuntimeError(f"download failed after {MAX_ATTEMPTS} attempts: {last_error}")


def load_sources():
    entries = []
    for file in sorted(SOURCES.glob("*.json")):
        payload = json.loads(file.read_text(encoding="utf-8"))
        for item in payload.get("channels", []):
            item = dict(item)
            item["_source_manifest"] = file.name
            entries.append(item)
    return entries


def validate_payload(item: dict, data: bytes, out: pathlib.Path) -> None:
    suffix = out.suffix.lower()
    if suffix == ".svg" and b"<svg" not in data[:4096].lower():
        raise RuntimeError("expected SVG payload")
    if suffix == ".png" and not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("expected PNG payload")
    if suffix == ".webp" and not (len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"):
        raise RuntimeError("expected WebP payload")
    if suffix not in {".svg", ".png", ".webp"}:
        raise RuntimeError(f"unsupported asset extension: {suffix}")


def main() -> None:
    channels = []
    failures = []
    attribution = [
        "# X1 Picons — Attribution & Source Register",
        "",
        "Generated automatically from `sources/*.json`.",
        "",
        "Channel names/logos may remain protected trademarks even when the file is freely reusable.",
        "",
    ]

    entries = load_sources()
    seen_ids = set()
    seen_paths = set()

    for item in entries:
        try:
            required = ["id", "name", "country", "category", "path", "url", "license", "sourcePage"]
            missing = [key for key in required if not item.get(key)]
            if missing:
                raise RuntimeError(f"missing {', '.join(missing)}")

            if item["id"] in seen_ids:
                raise RuntimeError("duplicate channel id")
            if item["path"] in seen_paths:
                raise RuntimeError("duplicate output path")

            host = urllib.parse.urlparse(item["url"]).hostname or ""
            if host not in ALLOWED_HOSTS:
                raise RuntimeError(f"source host not allowed: {host}")

            out = ROOT / item["path"]
            out.parent.mkdir(parents=True, exist_ok=True)
            data = fetch(item["url"])
            validate_payload(item, data, out)
            out.write_bytes(data)
            digest = hashlib.sha256(data).hexdigest()

            seen_ids.add(item["id"])
            seen_paths.add(item["path"])

            channels.append({
                "id": item["id"],
                "name": item["name"],
                "country": item["country"],
                "category": item["category"],
                "file": item["path"],
                "aliases": item.get("aliases", []),
                "status": "active",
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
        except Exception as exc:
            failures.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "country": item.get("country"),
                "manifest": item.get("_source_manifest"),
                "url": item.get("url"),
                "error": str(exc),
            })
            print(f"WARNING: skipped {item.get('id', '?')}: {exc}")

    now = datetime.now(timezone.utc).isoformat()
    channels.sort(key=lambda x: (x["country"], x["name"].casefold(), x["id"]))

    # Always persist diagnostics. This is intentionally written before the
    # fail-closed catalog guard so CI can publish useful failure evidence.
    REPORT.write_text(
        json.dumps({
            "generatedAt": now,
            "requested": len(entries),
            "synced": len(channels),
            "failed": len(failures),
            "catalogPublished": bool(channels),
            "failures": failures,
        }, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Requested {len(entries)} · synced {len(channels)} · failed {len(failures)}")

    # Fail closed: never replace the last known-good catalog/attribution with
    # an empty result merely because upstream downloads are unavailable.
    if not channels:
        raise SystemExit("No picons were synchronized; preserving last known-good catalog")

    INDEX.write_text(
        json.dumps({
            "schemaVersion": 1,
            "generatedAt": now,
            "channels": channels,
        }, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    ATTR.write_text("\n".join(attribution), encoding="utf-8")


if __name__ == "__main__":
    main()
