# X1 Picons

Modern, structured channel-logo library for the X1 ecosystem.

> **Migration status:** the historical PNG files in the repository root are preserved for compatibility while the new international library is populated and validated. Nothing from the legacy set is deleted until migration is confirmed.

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
├── data/
│   ├── schema.json
│   ├── index.json
│   └── legacy-duplicate-candidates.json
├── tools/
│   └── validate_index.py
└── legacy root PNGs (temporary compatibility)
```

## Asset standard

New picons should use:

- PNG or WebP with transparency where appropriate
- a consistent visual canvas
- lowercase file names
- ASCII-safe slugs
- no spaces
- no `(2)`, `copy`, `final2`, etc.
- stable IDs independent of the logo artwork
- ISO 3166-1 alpha-2 country codes

Recommended naming examples:

```text
rtp-1.png
sic.png
tve-1.png
antena-3.png
tf1.png
rai-1.png
bbc-one.png
sky-sports-main-event.png
```

## Canonical metadata

`data/index.json` is the machine-readable authority for the modern library. Apps and X1 panels should resolve picons by `id`, country and aliases rather than guessing from file names.

Example:

```json
{
  "id": "bbc-one",
  "name": "BBC One",
  "country": "GB",
  "category": "general",
  "file": "countries/gb/bbc-one.png",
  "aliases": ["BBC1", "BBC One HD"]
}
```

## Migration policy

1. Keep all historical root files untouched.
2. Add current logos into the new structure.
3. Add validated metadata to `data/index.json`.
4. Detect byte-identical and semantic duplicates.
5. Verify consumers can resolve the new paths.
6. Only then deprecate or remove legacy assets in a separate reviewed change.

See [MIGRATION.md](./MIGRATION.md).

## Countries — first wave

The first international expansion targets:

**Portugal · Spain · France · Italy · Germany · United Kingdom · Switzerland · Belgium · Netherlands · Brazil · USA**

Additional countries can be introduced without changing the schema.

## Trademark / asset note

Channel names and logos may be trademarks of their respective owners. Only add assets that X1 is permitted to redistribute, including broadcaster-provided press assets or other appropriately licensed sources.

---

**X1 · One ecosystem. One identity.**
