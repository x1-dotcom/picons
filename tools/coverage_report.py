#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
OUT_JSON = ROOT / "data" / "coverage.json"
OUT_MD = ROOT / "COVERAGE.md"


def load_definitions() -> list[dict]:
    rows: list[dict] = []
    for manifest in sorted(SOURCES.glob("*.json")):
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        for item in payload.get("channels", []):
            row = dict(item)
            row["sourceManifest"] = manifest.name
            rows.append(row)
    return rows


def main() -> None:
    definitions = load_definitions()
    by_country: dict[str, dict] = defaultdict(lambda: {
        "defined": 0,
        "materialized": 0,
        "missing": 0,
        "categories": Counter(),
    })
    missing_assets: list[dict] = []

    for item in definitions:
        country = item["country"]
        target = ROOT / item["path"]
        by_country[country]["defined"] += 1
        by_country[country]["categories"][item["category"]] += 1
        if target.is_file():
            by_country[country]["materialized"] += 1
        else:
            by_country[country]["missing"] += 1
            missing_assets.append({
                "id": item["id"],
                "name": item["name"],
                "country": country,
                "path": item["path"],
                "sourceManifest": item["sourceManifest"],
            })

    country_rows = []
    for country in sorted(by_country):
        row = by_country[country]
        defined = row["defined"]
        materialized = row["materialized"]
        country_rows.append({
            "country": country,
            "defined": defined,
            "materialized": materialized,
            "missing": row["missing"],
            "materializationPercent": round((materialized / defined * 100.0), 1) if defined else 0.0,
            "categories": dict(sorted(row["categories"].items())),
        })

    generated_at = datetime.now(timezone.utc).isoformat()
    payload = {
        "generatedAt": generated_at,
        "definedTotal": len(definitions),
        "materializedTotal": sum(x["materialized"] for x in country_rows),
        "missingTotal": sum(x["missing"] for x in country_rows),
        "countries": country_rows,
        "missingAssets": sorted(missing_assets, key=lambda x: (x["country"], x["name"].casefold(), x["id"])),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# X1 Picons — Coverage Matrix",
        "",
        f"Generated: `{generated_at}`",
        "",
        "This report deliberately separates **DEFINED IN MANIFEST** from **ACTUALLY MATERIALIZED** assets.",
        "",
        f"- Defined channels: **{payload['definedTotal']}**",
        f"- Materialized assets: **{payload['materializedTotal']}**",
        f"- Missing assets: **{payload['missingTotal']}**",
        "",
        "| Country | Defined | Materialized | Missing | Materialized % |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in country_rows:
        lines.append(
            f"| {row['country']} | {row['defined']} | {row['materialized']} | {row['missing']} | {row['materializationPercent']:.1f}% |"
        )

    lines.extend(["", "## Missing materialized assets", ""])
    if missing_assets:
        for item in payload["missingAssets"]:
            lines.append(f"- `{item['country']}` · **{item['name']}** · `{item['path']}` · `{item['sourceManifest']}`")
    else:
        lines.append("All manifest definitions are materialized.")

    lines.extend([
        "",
        "## Interpretation",
        "",
        "A high manifest count does not mean the picon is already published. Consumers should use `data/index.json` as runtime authority and this report as migration/coverage telemetry.",
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Coverage: defined={payload['definedTotal']} materialized={payload['materializedTotal']} missing={payload['missingTotal']}")


if __name__ == "__main__":
    main()
