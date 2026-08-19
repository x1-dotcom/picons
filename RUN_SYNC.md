# X1 Picons — Sync Runbook

This runbook is the operational path for materializing the modern picon catalog from `sources/*.json` into `countries/<cc>/`.

## Immediate manual run

1. Open the repository **Actions** tab.
2. Select **Sync X1 Picons**.
3. Choose **Run workflow**.
4. Run it against `main`.
5. Wait for the job to finish.

The workflow also runs on its schedule and on supported source/tool changes, but an explicit manual run is the fastest way to prove the end-to-end path after repository changes made through APIs or automation.

## Expected successful outputs

A GREEN run should publish/update:

- `countries/<cc>/*` — materialized picon assets
- `data/index.json` — runtime authority
- `data/sync-report.json` — requested/synced/failed source report
- `data/coverage.json` — defined vs materialized matrix
- `data/legacy-audit.json` — legacy root audit
- `ATTRIBUTION.md` — source/license register
- `COVERAGE.md` — human-readable coverage matrix

The success commit should normally be named:

`Sync current X1 picons`

## Failure behavior

The pipeline is fail-closed.

If synchronization fails:

- it must not replace the last known-good `data/index.json` with an empty catalog;
- it preserves diagnostics in `data/sync-report.json`;
- it still generates coverage and legacy-audit telemetry;
- the workflow remains failed/red so the error is visible.

A diagnostic commit may be named:

`Record X1 picon sync failure diagnostics`

## What to inspect first after a failed run

1. `data/sync-report.json` → exact failing channel/source URL and error.
2. `data/coverage.json` → definitions that remain unmaterialized.
3. `data/legacy-audit.json` → exact legacy duplicates and naming anomalies.
4. Workflow job logs → manifest validation, download, payload validation, index validation or git-push failure.

## Safety rules

- Never delete a legacy picon only because the filename looks duplicated.
- Byte-identical files may be cleanup candidates after compatibility review.
- Differing variants require visual/semantic review.
- Do not publish assets from sources with unclear redistribution rights.
- `data/index.json` is the runtime authority; manifests are definitions, not proof that an asset has been published.

## Local validation commands

```bash
python tools/audit_manifests.py
python tools/audit_legacy.py
python tools/coverage_report.py
python tools/validate_index.py
```

`validate_index.py` is expected to validate a materialized catalog, including actual SHA-256 checks against the files on disk.

---

**X1 · Controlled sources · Reproducible catalog · Safe migration**
