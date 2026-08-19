#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "data" / "legacy-migration-pt.json"
OUT_JSON = ROOT / "data" / "compatibility-checklist-pt.json"
OUT_MD = ROOT / "COMPATIBILITY_PORTUGAL.md"


def main() -> None:
    migration = json.loads(MIGRATION.read_text(encoding="utf-8"))
    rows = []
    for item in migration.get("mappings", []):
        status = item.get("status")
        if status not in {"READY_FOR_COMPAT_TEST", "READY_FOR_REMOVAL"}:
            continue
        rows.append({
            "legacyFile": item.get("legacyFile"),
            "modernId": item.get("modernId"),
            "modernPath": item.get("modernPath"),
            "status": status,
            "materializationEvidence": item.get("materializationEvidence"),
            "checks": {
                "legacyResolverWorks": None,
                "modernResolverWorks": None,
                "aliasResolutionWorks": None,
                "uiRendersCorrectly": None,
                "noBrokenConsumerReferences": None,
            },
            "decision": "PENDING",
            "notes": "",
        })

    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "schemaVersion": 1,
        "country": "PT",
        "generatedAt": now,
        "policy": "This file is a compatibility-test checklist only. It never authorizes deletion by itself.",
        "items": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    counts = Counter(x["status"] for x in rows)
    lines = [
        "# X1 Picons — Portugal Compatibility Checklist",
        "",
        f"Generated: `{now}`",
        "",
        "This checklist is generated only for mappings that reached `READY_FOR_COMPAT_TEST` or `READY_FOR_REMOVAL`.",
        "It does **not** delete files and it does **not** promote anything to removal automatically.",
        "",
        f"- Ready for compatibility test: **{counts.get('READY_FOR_COMPAT_TEST', 0)}**",
        f"- Already approved for removal: **{counts.get('READY_FOR_REMOVAL', 0)}**",
        "",
        "## Required checks before any removal",
        "",
        "For each candidate verify:",
        "",
        "- legacy resolver still resolves during the transition",
        "- modern resolver returns the new `modernId` / path",
        "- aliases resolve correctly",
        "- UI/player renders the new picon correctly",
        "- no consumer still references the root legacy filename directly",
        "",
        "## Candidates",
        "",
    ]
    if not rows:
        lines.append("No mapping is ready for compatibility testing yet.")
    else:
        for row in rows:
            lines.extend([
                f"### `{row['legacyFile']}` → `{row['modernId']}`",
                "",
                f"Modern asset: `{row['modernPath']}`",
                f"Status: **{row['status']}**",
                "",
                "- [ ] legacy resolver works during transition",
                "- [ ] modern resolver works",
                "- [ ] aliases resolve",
                "- [ ] UI/player renders correctly",
                "- [ ] no broken direct references remain",
                "- [ ] explicit owner approval recorded before removal",
                "",
            ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Portugal compatibility checklist: {len(rows)} candidate(s)")


if __name__ == "__main__":
    main()
