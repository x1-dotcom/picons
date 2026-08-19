# X1 Picons

Modern, structured channel-logo library for the X1 ecosystem.

> **Migration status:** the historical PNG files in the repository root are preserved for compatibility while the new international library is populated and validated. Legacy files are removed only after duplicate/replacement coverage is confirmed.

## New library structure

```text
picons/
├── countries/
│   ├── pt/          # Portugal
│   ├── es/          # Spain
│   ├── fr/          # France
│   ├── it/          # Italy
│   ├── de/          # Germany
│   ├── gb/          # United Kingdom
│   ├── ch/          # Switzerland
│   ├── be/          # Belgium
│   ├── nl/          # Netherlands
│   ├── br/          # Brazil
│   └── us/          # United States
├── categories/
│   ├── sports/
│   ├── movies/
│   ├── kids/
│   ├── news/
│   └── music/
├── sources/         # approved source manifests
├── data/
│   ├── schema.json
│   ├── index.json
│   ├── sync-report.json
│   └── legacy-duplicate-candidates.json
├── tools/
│   ├── audit_manifests.py
│   ├── sync_sources.py
│   └── validate_index.py
└── legacy root PNGs (temporary compatibility)
```

## Asset standard

New picons may use:

- SVG where a clean vector source is available
- PNG or WebP with transparency where appropriate
- lowercase file names
- ASCII-safe slugs
- no spaces
- no `(2)`, `copy`, `final2`, etc.
- stable IDs independent of the logo artwork
- ISO 3166-1 alpha-2 country codes

Recommended naming examples:

```text
rtp-1.svg
sic-noticias.svg
la-1.svg
antena-3.svg
france-2.svg
rai-1.svg
bbc-one.svg
sport-tv-1.svg
```

## Source manifests

Every modern picon starts from an approved `sources/*.json` manifest. Each channel definition records its stable ID, country, category, target path, source URL, source page, licensing/status note, trademark flag and aliases.

`tools/audit_manifests.py` validates the manifests before any network download. It rejects malformed JSON, duplicate IDs or output paths, unsafe paths, non-HTTPS sources, unsupported hosts/extensions, country/path mismatches and alias collisions.

## Canonical metadata

`data/index.json` is the machine-readable authority for the modern library. Apps and X1 panels should resolve picons by `id`, country and aliases rather than guessing from file names.

Example:

```json
{
  "id": "bbc-one",
  "name": "BBC One",
  "country": "GB",
  "category": "general",
  "file": "countries/gb/bbc-one.svg",
  "aliases": ["BBC1", "BBC One HD"]
}
```

## Automated synchronization

The GitHub workflow audits source manifests, downloads approved assets, validates payload type and size, computes SHA-256, regenerates `data/index.json`, writes `data/sync-report.json` and maintains `ATTRIBUTION.md`.

The sync is configured for manual execution, manifest/tool changes and a six-hour schedule.

## Migration policy

1. Keep historical root assets while they are still needed for compatibility.
2. Add current logos through approved source manifests.
3. Materialize and validate assets in `countries/<cc>/`.
4. Generate the canonical `data/index.json`.
5. Detect byte-identical and semantic duplicates.
6. Verify consumers can resolve the new paths.
7. Remove obsolete legacy assets only when replacement or duplicate status is confirmed.

See [MIGRATION.md](./MIGRATION.md).

## Countries — first wave

**Portugal · Spain · France · Italy · Germany · United Kingdom · Switzerland · Belgium · Netherlands · Brazil · USA**

Additional countries can be introduced without changing the schema.

## Trademark / asset note

Channel names and logos may be trademarks of their respective owners. Only add assets that X1 is permitted to redistribute, including broadcaster-provided press assets or other appropriately licensed sources.

---

**X1 · One ecosystem. One identity.**
