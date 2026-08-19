#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "index.json"
MIGRATION = ROOT / "data" / "legacy-migration-pt.json"
OUT_JSON = ROOT / "data" / "removal-dry-run-pt.json"
OUT_MD = ROOT / "REMOVAL_DRY_RUN_PORTUGAL.md"


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

    now = datetime.now(timezone.utc).isoformat()
    candidates = []
    blocked = []

    for mapping in migration.get("mappings", []):
        if mapping.get("status") != "READY_FOR_REMOVAL":
            continue

        legacy_name = mapping.get("legacyFile")
        modern_id = mapping.get("modernId")
        modern_path = mapping.get("modernPath")
        reasons = []

        if not legacy_name or Path(legacy_name).name != legacy_name or Path(legacy_name).is_absolute():
            reasons.append("legacy filename is not a safe root filename")
            legacy_path = None
        else:
            legacy_path = ROOT / legacy_name

        indexed_item = indexed.get(modern_id)
        modern_asset = ROOT / modern_path if modern_path else None

        if legacy_path is None or not legacy_path.is_file():
            reasons.append("legacy root file does not exist")
        if indexed_item is None:
            reasons.append("modernId is not present in data/index.json")
        elif indexed_item.get("file") != modern_path:
            reasons.append("modern path differs from current index")
        if modern_asset is None or not modern_asset.is_file():
            reasons.append("modern asset is not materialized")

        modern_sha = None
        if modern_asset is not None and modern_asset.is_file() and indexed_item is not None:
            modern_sha = sha256_file(modern_asset)
            if indexed_item.get("sha256") != modern_sha:
                reasons.append("modern asset SHA-256 differs from current index")

        approval = mapping.get("removalApproval") or {}
        if not approval.get("approvedBy") or not approval.get("approvedAt"):
            reasons.append("verified removal approval evidence is missing")
        if modern_sha and approval.get("modernSha256") != modern_sha:
            reasons.append("approval SHA-256 differs from current modern asset")

        legacy_sha = sha256_file(legacy_path) if legacy_path is not None and legacy_path.is_file() else None
        row = {
            "legacyFile": legacy_name,
            "legacySha256": legacy_sha,
            "modernId": modern_id,
            "modernPath": modern_path,
            "modernSha256": modern_sha,
            "approvedBy": approval.get("approvedBy"),
            "approvedAt": approval.get("approvedAt"),
            "approvalReference": approval.get("approvalReference"),
            "action": "WOULD_DELETE_LEGACY_ROOT_FILE" if not reasons else "BLOCKED",
            "blockers": reasons,
        }

        if reasons:
            blocked.append(row)
        else:
            candidates.append(row)

    payload = {
        "schemaVersion": 1,
        "country": "PT",
        "generatedAt": now,
        "mode": "DRY_RUN_ONLY",
        "policy": "This report never deletes files. Only mappings already READY_FOR_REMOVAL with current approval/index/path/hash evidence may appear as deletion candidates.",
        "candidateCount": len(candidates),
        "blockedCount": len(blocked),
        "candidates": candidates,
        "blocked": blocked,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# X1 Picons — Portugal Legacy Removal Dry Run",
        "",
        f"Generated: `{now}`",
        "",
        "**Mode: DRY RUN ONLY — no file is deleted by this tool.**",
        "",
        f"- Would delete: **{len(candidates)}**",
        f"- Blocked: **{len(blocked)}**",
        "",
        "## Would delete",
        "",
    ]

    if not candidates:
        lines.append("No legacy file is currently eligible for removal.")
    else:
        for row in candidates:
            lines.extend([
                f"### `{row['legacyFile']}` → `{row['modernId']}`",
                "",
                f"- Legacy SHA-256: `{row['legacySha256']}`",
                f"- Modern asset: `{row['modernPath']}`",
                f"- Modern SHA-256: `{row['modernSha256']}`",
                f"- Approved by: `{row['approvedBy']}`",
                f"- Approved at: `{row['approvedAt']}`",
                "",
            ])

    lines.extend(["", "## Blocked READY_FOR_REMOVAL mappings", ""])
    if not blocked:
        lines.append("No blocked READY_FOR_REMOVAL mapping.")
    else:
        for row in blocked:
            lines.append(f"- `{row['legacyFile']}`: " + "; ".join(row["blockers"]))

    lines.extend([
        "",
        "## Execution policy",
        "",
        "Actual deletion must remain a separate explicit operation. A deletion executor must re-verify the same evidence immediately before removing each root file and must fail closed on any mismatch.",
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Portugal removal dry run: candidates={len(candidates)} blocked={len(blocked)}")


if __name__ == "__main__":
    main()
