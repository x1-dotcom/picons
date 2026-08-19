#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "legacy-audit.json"
COPY_SUFFIX = re.compile(r"\s*\((?:copy|\d+)\)$", re.IGNORECASE)
SAFE_NAME = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*\.png$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalized_stem(path: Path) -> str:
    stem = COPY_SUFFIX.sub("", path.stem).strip().casefold()
    return re.sub(r"[^a-z0-9]+", "", stem)


def main() -> None:
    files = sorted(p for p in ROOT.glob("*.png") if p.is_file())
    by_hash: dict[str, list[str]] = defaultdict(list)
    by_normalized_name: dict[str, list[str]] = defaultdict(list)
    anomalies: list[dict] = []

    for path in files:
        digest = sha256(path)
        by_hash[digest].append(path.name)
        by_normalized_name[normalized_stem(path)].append(path.name)

        reasons = []
        if not SAFE_NAME.fullmatch(path.name):
            reasons.append("non-canonical-filename")
        if re.search(r"\(\d+\)", path.name):
            reasons.append("copy-suffix")
        if any(ch.isupper() for ch in path.name):
            reasons.append("uppercase")
        if " " in path.name:
            reasons.append("space")
        if any(ord(ch) > 127 for ch in path.name):
            reasons.append("non-ascii")
        if any(ch in path.name for ch in "~!+"):
            reasons.append("special-character")

        if reasons:
            anomalies.append({"file": path.name, "reasons": sorted(set(reasons))})

    exact_duplicates = []
    for digest, names in sorted(by_hash.items()):
        if len(names) > 1:
            exact_duplicates.append({
                "sha256": digest,
                "files": sorted(names),
                "classification": "SAFE_DUPLICATE_CANDIDATE",
                "action": "KEEP_ONE_AFTER_COMPATIBILITY_REVIEW",
            })

    visual_review = []
    exact_sets = {tuple(sorted(x["files"])) for x in exact_duplicates}
    for key, names in sorted(by_normalized_name.items()):
        unique = sorted(set(names))
        if len(unique) < 2:
            continue
        if tuple(unique) in exact_sets:
            continue
        visual_review.append({
            "normalizedName": key,
            "files": unique,
            "classification": "NEEDS_VISUAL_REVIEW",
            "action": "DO_NOT_AUTO_DELETE",
        })

    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "policy": "Audit only. This tool never deletes files.",
        "rootPngCount": len(files),
        "exactDuplicateGroups": exact_duplicates,
        "visualReviewGroups": visual_review,
        "filenameAnomalies": sorted(anomalies, key=lambda x: x["file"].casefold()),
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"Legacy audit: root_pngs={len(files)} exact_duplicate_groups={len(exact_duplicates)} "
        f"visual_review_groups={len(visual_review)} filename_anomalies={len(anomalies)}"
    )


if __name__ == "__main__":
    main()
