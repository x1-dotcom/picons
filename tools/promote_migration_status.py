#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "index.json"
MIGRATION = ROOT / "data" / "legacy-migration-pt.json"

AUTO_PROMOTABLE = {"WAIT_MATERIALIZATION", "READY_FOR_COMPAT_TEST"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    migration = json.loads(MIGRATION.read_text(encoding="utf-8"))

    indexed = {item["id"]: item for item in index.get("channels", [])}
    promoted = 0
    waiting = 0

    now = datetime.now(timezone.utc).isoformat()

    for mapping in migration.get("mappings", []):
        status = mapping.get("status")
        modern_id = mapping.get("modernId")
        modern_path = mapping.get("modernPath")

        if status not in AUTO_PROMOTABLE or not modern_id or not modern_path:
            continue

        item = indexed.get(modern_id)
        asset = ROOT / modern_path
        evidence_ok = False
        reason = None

        if item is None:
            reason = "modernId is not present in data/index.json"
        elif item.get("file") != modern_path:
            reason = "index file path does not match migration modernPath"
        elif not asset.is_file():
            reason = "modern asset is not materialized"
        else:
            actual_sha = sha256_file(asset)
            indexed_sha = item.get("sha256")
            if actual_sha != indexed_sha:
                reason = "materialized asset SHA-256 does not match index"
            else:
                evidence_ok = True

        if evidence_ok:
            if status == "WAIT_MATERIALIZATION":
                mapping["status"] = "READY_FOR_COMPAT_TEST"
                promoted += 1
            mapping["materializationEvidence"] = {
                "verifiedAt": now,
                "modernId": modern_id,
                "modernPath": modern_path,
                "sha256": item["sha256"],
                "indexStatus": item.get("status"),
            }
        else:
            if status == "READY_FOR_COMPAT_TEST":
                mapping["status"] = "WAIT_MATERIALIZATION"
            mapping.pop("materializationEvidence", None)
            waiting += 1
            if reason:
                mapping["materializationBlocker"] = reason
        if evidence_ok:
            mapping.pop("materializationBlocker", None)

    migration["lastMaterializationCheckAt"] = now
    migration["automaticPromotionPolicy"] = (
        "Automation may only move WAIT_MATERIALIZATION to READY_FOR_COMPAT_TEST after index/path/hash verification. "
        "READY_FOR_REMOVAL always requires an explicit compatibility decision and is never set automatically."
    )

    MIGRATION.write_text(json.dumps(migration, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Migration materialization check: promoted={promoted} waiting_or_blocked={waiting}")


if __name__ == "__main__":
    main()
