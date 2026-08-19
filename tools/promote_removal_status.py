#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "index.json"
MIGRATION = ROOT / "data" / "legacy-migration-pt.json"
APPROVALS = ROOT / "data" / "removal-approvals-pt.json"

REQUIRED_CHECKS = {
    "legacyResolverWorks",
    "modernResolverWorks",
    "aliasResolutionWorks",
    "uiRendersCorrectly",
    "noBrokenConsumerReferences",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    migration = json.loads(MIGRATION.read_text(encoding="utf-8"))
    approvals_payload = json.loads(APPROVALS.read_text(encoding="utf-8"))

    indexed = {item["id"]: item for item in index.get("channels", [])}
    mappings = {item.get("legacyFile"): item for item in migration.get("mappings", [])}

    seen_legacy = set()
    promoted = 0
    rejected = 0
    now = datetime.now(timezone.utc).isoformat()

    for approval in approvals_payload.get("approvals", []):
        legacy_file = approval.get("legacyFile")
        modern_id = approval.get("modernId")
        modern_sha = approval.get("modernSha256")
        approved = approval.get("approved") is True
        checks = approval.get("compatibilityChecks", {})

        if not legacy_file or legacy_file in seen_legacy:
            rejected += 1
            continue
        seen_legacy.add(legacy_file)

        mapping = mappings.get(legacy_file)
        if mapping is None or mapping.get("status") not in {"READY_FOR_COMPAT_TEST", "READY_FOR_REMOVAL"}:
            rejected += 1
            continue
        if mapping.get("modernId") != modern_id:
            rejected += 1
            continue
        if not approved:
            rejected += 1
            continue
        if not all(checks.get(name) is True for name in REQUIRED_CHECKS):
            rejected += 1
            continue
        if not approval.get("approvedBy") or not approval.get("approvedAt"):
            rejected += 1
            continue

        indexed_item = indexed.get(modern_id)
        modern_path = mapping.get("modernPath")
        if indexed_item is None or indexed_item.get("file") != modern_path:
            rejected += 1
            continue

        asset = ROOT / modern_path
        if not asset.is_file():
            rejected += 1
            continue

        actual_sha = sha256_file(asset)
        if indexed_item.get("sha256") != actual_sha or modern_sha != actual_sha:
            rejected += 1
            continue

        if mapping.get("status") != "READY_FOR_REMOVAL":
            mapping["status"] = "READY_FOR_REMOVAL"
            promoted += 1
        mapping["removalApproval"] = {
            "verifiedAt": now,
            "approvedBy": approval["approvedBy"],
            "approvedAt": approval["approvedAt"],
            "approvalReference": approval.get("approvalReference"),
            "modernSha256": actual_sha,
            "compatibilityChecks": {name: True for name in sorted(REQUIRED_CHECKS)},
        }

    migration["lastRemovalApprovalCheckAt"] = now
    migration["removalPromotionPolicy"] = (
        "READY_FOR_REMOVAL requires an explicit entry in data/removal-approvals-pt.json, all compatibility checks true, "
        "and current index/path/SHA-256 verification. This script never deletes files."
    )
    MIGRATION.write_text(json.dumps(migration, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Portugal removal approvals: promoted={promoted} rejected_or_not_ready={rejected}")


if __name__ == "__main__":
    main()
