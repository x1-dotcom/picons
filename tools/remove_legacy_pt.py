#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "index.json"
MIGRATION = ROOT / "data" / "legacy-migration-pt.json"
APPROVALS = ROOT / "data" / "removal-approvals-pt.json"
RECEIPT = ROOT / "data" / "removal-receipt-pt.json"
CONFIRM_TOKEN = "X1-REMOVE-APPROVED-PT"

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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_root_file(name: str | None) -> Path | None:
    if not name:
        return None
    p = Path(name)
    if p.is_absolute() or p.name != name or ".." in p.parts:
        return None
    return ROOT / name


def validate_mapping(mapping: dict, index_by_id: dict, approval_by_legacy: dict) -> tuple[list[str], dict]:
    blockers: list[str] = []
    legacy_name = mapping.get("legacyFile")
    modern_id = mapping.get("modernId")
    modern_path = mapping.get("modernPath")

    if mapping.get("status") != "READY_FOR_REMOVAL":
        blockers.append("mapping status is not READY_FOR_REMOVAL")

    legacy_path = safe_root_file(legacy_name)
    if legacy_path is None:
        blockers.append("legacy filename is not a safe repository-root filename")
    elif not legacy_path.is_file():
        blockers.append("legacy root file does not exist")

    indexed = index_by_id.get(modern_id)
    if indexed is None:
        blockers.append("modernId is not present in data/index.json")
    elif indexed.get("file") != modern_path:
        blockers.append("modernPath differs from current index")

    modern_asset = ROOT / modern_path if modern_path else None
    if modern_asset is None or not modern_asset.is_file():
        blockers.append("modern asset is not materialized")

    legacy_sha = sha256_file(legacy_path) if legacy_path is not None and legacy_path.is_file() else None
    modern_sha = sha256_file(modern_asset) if modern_asset is not None and modern_asset.is_file() else None

    if indexed is not None and modern_sha is not None and indexed.get("sha256") != modern_sha:
        blockers.append("modern asset SHA-256 differs from current index")

    verified = mapping.get("removalApproval") or {}
    if not verified.get("approvedBy") or not verified.get("approvedAt"):
        blockers.append("verified removalApproval evidence is missing from migration mapping")
    if modern_sha is not None and verified.get("modernSha256") != modern_sha:
        blockers.append("migration removalApproval SHA-256 differs from current modern asset")

    approval = approval_by_legacy.get(legacy_name)
    if approval is None:
        blockers.append("explicit approval entry is missing")
    else:
        if approval.get("approved") is not True:
            blockers.append("explicit approval is not true")
        if approval.get("modernId") != modern_id:
            blockers.append("explicit approval modernId differs from migration")
        if not approval.get("approvedBy") or not approval.get("approvedAt"):
            blockers.append("explicit approval lacks approvedBy/approvedAt")
        checks = approval.get("compatibilityChecks") or {}
        if not all(checks.get(name) is True for name in REQUIRED_CHECKS):
            blockers.append("not all compatibility checks are true")
        if modern_sha is not None and approval.get("modernSha256") != modern_sha:
            blockers.append("explicit approval SHA-256 differs from current modern asset")

    evidence = {
        "legacyFile": legacy_name,
        "legacySha256": legacy_sha,
        "modernId": modern_id,
        "modernPath": modern_path,
        "modernSha256": modern_sha,
        "approvedBy": approval.get("approvedBy") if approval else None,
        "approvedAt": approval.get("approvedAt") if approval else None,
        "approvalReference": approval.get("approvalReference") if approval else None,
    }
    return blockers, evidence


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Guarded removal executor for approved Portugal legacy root picons. Dry-run is the default."
    )
    parser.add_argument("--execute", action="store_true", help="Actually remove eligible legacy root files")
    parser.add_argument(
        "--confirm",
        default="",
        help=f"Required with --execute. Must equal {CONFIRM_TOKEN!r}",
    )
    args = parser.parse_args()

    if args.execute and args.confirm != CONFIRM_TOKEN:
        print(f"ERROR: --execute requires --confirm {CONFIRM_TOKEN}", file=sys.stderr)
        raise SystemExit(2)

    index = load_json(INDEX)
    migration = load_json(MIGRATION)
    approvals = load_json(APPROVALS)

    index_by_id = {item.get("id"): item for item in index.get("channels", [])}
    approval_by_legacy: dict[str, dict] = {}
    duplicate_approvals = set()
    for approval in approvals.get("approvals", []):
        legacy = approval.get("legacyFile")
        if not legacy:
            continue
        if legacy in approval_by_legacy:
            duplicate_approvals.add(legacy)
        approval_by_legacy[legacy] = approval

    now = datetime.now(timezone.utc).isoformat()
    eligible: list[dict] = []
    blocked: list[dict] = []
    removed: list[dict] = []

    for mapping in migration.get("mappings", []):
        if mapping.get("status") not in {"READY_FOR_REMOVAL", "REMOVED"}:
            continue
        if mapping.get("status") == "REMOVED":
            continue

        blockers, evidence = validate_mapping(mapping, index_by_id, approval_by_legacy)
        if evidence["legacyFile"] in duplicate_approvals:
            blockers.append("duplicate explicit approval entries exist for this legacy file")

        if blockers:
            row = dict(evidence)
            row["blockers"] = blockers
            blocked.append(row)
            continue

        eligible.append(dict(evidence))

        if args.execute:
            legacy_path = ROOT / evidence["legacyFile"]

            # Revalidate immediately before deletion to reduce TOCTOU risk.
            blockers_now, evidence_now = validate_mapping(mapping, index_by_id, approval_by_legacy)
            if blockers_now:
                row = dict(evidence_now)
                row["blockers"] = ["pre-delete revalidation failed"] + blockers_now
                blocked.append(row)
                continue
            if evidence_now["legacySha256"] != evidence["legacySha256"]:
                row = dict(evidence_now)
                row["blockers"] = ["legacy file changed between planning and execution"]
                blocked.append(row)
                continue

            legacy_path.unlink()
            if legacy_path.exists():
                raise RuntimeError(f"legacy file still exists after unlink: {legacy_path}")

            mapping["status"] = "REMOVED"
            mapping["removalReceipt"] = {
                "removedAt": now,
                "legacySha256": evidence["legacySha256"],
                "modernId": evidence["modernId"],
                "modernPath": evidence["modernPath"],
                "modernSha256": evidence["modernSha256"],
                "approvedBy": evidence["approvedBy"],
                "approvedAt": evidence["approvedAt"],
                "approvalReference": evidence["approvalReference"],
            }
            removed.append(dict(evidence))

    mode = "EXECUTE" if args.execute else "DRY_RUN"
    receipt = {
        "schemaVersion": 1,
        "country": "PT",
        "generatedAt": now,
        "mode": mode,
        "policy": "Execution is fail-closed. Only READY_FOR_REMOVAL mappings with current index/path/hash and explicit compatibility approval may be removed.",
        "eligibleCount": len(eligible),
        "blockedCount": len(blocked),
        "removedCount": len(removed),
        "eligible": eligible,
        "blocked": blocked,
        "removed": removed,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.execute:
        migration["lastRemovalExecutionAt"] = now
        migration["removalExecutionPolicy"] = (
            "Legacy deletion requires --execute plus the explicit confirmation token and immediate pre-delete revalidation."
        )
        MIGRATION.write_text(json.dumps(migration, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        f"Portugal legacy removal {mode}: eligible={len(eligible)} blocked={len(blocked)} removed={len(removed)}"
    )
    if not args.execute:
        print(f"Dry-run only. To execute, use: --execute --confirm {CONFIRM_TOKEN}")


if __name__ == "__main__":
    main()
