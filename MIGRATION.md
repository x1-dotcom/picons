# X1 Picons Migration Plan

## Goal

Move the legacy Portugal-heavy flat collection into a clean international library without breaking existing consumers.

## Phase A — Foundation

- keep legacy root files untouched
- introduce country/category directories
- define canonical metadata schema
- introduce machine-readable index
- introduce validation tooling
- record duplicate candidates without deleting anything

## Phase B — Portugal refresh

- validate current Portuguese channel lineup
- replace stale artwork only from permitted sources
- normalize filenames and dimensions
- preserve aliases for historical names
- record superseded legacy filenames

## Phase C — International expansion

Priority order:

1. Spain
2. France
3. Italy
4. Germany
5. United Kingdom
6. Switzerland
7. Belgium
8. Netherlands
9. Brazil
10. USA

## Phase D — Categories

Cross-country curated sets:

- sports
- movies
- kids
- news
- music

Country remains authoritative in metadata. Category folders are optional curated views, not duplicated metadata authority.

## Phase E — Compatibility migration

Before deleting any legacy file:

- prove its canonical replacement exists
- confirm aliases cover old naming
- verify raw GitHub consumers/panels use the index or new path
- publish a deprecation map
- keep a compatibility window

## Naming rules

Canonical asset names use lowercase kebab-case:

`bbc-one.png`

Do not use:

`BBC One HD FINAL (2).png`

## Duplicate policy

Three classifications are used:

- **BYTE_IDENTICAL** — same SHA/blob content
- **VISUAL_DUPLICATE** — same logo artwork but encoded differently
- **SEMANTIC_ALIAS** — different artwork or naming for the same channel identity

Only BYTE_IDENTICAL files can be considered mechanically redundant. Even then, removal waits for compatibility validation.

## Status

Foundation: **IN PROGRESS**

Legacy deletion: **NOT STARTED**
