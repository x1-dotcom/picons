<p align="center">
  <img src="./assets/x1-picons-hero.svg" alt="X1 Picons" width="100%" />
</p>

<p align="center">
  <strong>PUBLIC · COMMUNITY · VISUAL DATA</strong><br>
  Stable channel identity, country-aware artwork, source traceability and explicit rights notes.
</p>

<p align="center">
  <a href="https://x1panelhq.com"><strong>WEBSITE</strong></a>
  &nbsp;·&nbsp;
  <a href="https://forum.x1panelhq.com"><strong>FORUM</strong></a>
  &nbsp;·&nbsp;
  <a href="https://discord.gg/vSSw6jHmw"><strong>DISCORD</strong></a>
  &nbsp;·&nbsp;
  <a href="https://t.me/+XkuQS_QuD6g4Nzc0"><strong>TELEGRAM</strong></a>
</p>

---

## X1 Picons

**X1 Picons is the public visual-signal catalogue used across the X1 ecosystem.**

> **Free means functional.**
> The public project is intended to be useful as released while keeping identity, provenance and rights explicit.

It is built around stable channel identities, country-aware organization, source traceability and explicit rights notes — not around an uncontrolled folder of logo files.

> **Current migration state:** the old root PNG dump has been removed. The repository now uses the structured X1 layout under `countries/`, `categories/`, `sources/`, `data/` and `tools/`.

<p align="center">
  <img src="./assets/x1-picons-capabilities.svg" alt="X1 Picons capability surface" width="100%" />
</p>

---

<p align="center">
  <img src="./assets/x1-picons-model.svg" alt="X1 Picons Canonical Model" width="100%" />
</p>

## Canonical model

A picon is not identified by whatever filename happens to exist today. X1 treats the stable channel identity as the primary key. Artwork can change without forcing consuming applications to change their canonical channel IDs.

Typical identity fields include:

- stable `id`;
- ISO 3166-1 alpha-2 country scope;
- channel name and aliases;
- category;
- canonical target path;
- source URL / source page;
- rights or licensing note;
- trademark note where relevant.

Consumers should resolve assets by **ID + country + aliases**, not by guessing filenames.

---

## Operating model

`IDENTIFY` → `SOURCE` → `AUDIT` → `MATERIALIZE` → `VALIDATE` → `PUBLISH WHEN ALLOWED`

> **Manifest present ≠ asset materialized ≠ consumer verified.**

Each state should be proven independently.

---

## Repository structure

```text
picons/
├── countries/       # country-scoped picon library
├── categories/      # category views / organization
├── sources/         # source manifests and provenance metadata
├── data/            # canonical indexes and validation reports
├── tools/           # validation, synchronization and coverage tooling
├── .github/         # automation
├── README.md
├── RUN_SYNC.md
└── migration documentation
```

The legacy root-image layout is no longer the active model.

---

## Countries

The structured catalogue currently includes source/manifests work across multiple markets, including:

**Portugal · Spain · France · Germany · Italy · United Kingdom · Switzerland · Netherlands · Belgium · Brazil**

Additional countries can be introduced without changing the canonical identity model.

Country directories use lower-case ISO-based paths such as:

```text
countries/pt/
countries/es/
countries/fr/
countries/de/
countries/it/
countries/gb/
countries/ch/
countries/nl/
```

---

## Asset rules

Modern X1 picons may use SVG, PNG or WebP when appropriate.

Naming and organization follow these rules:

- lower-case, ASCII-safe slugs;
- no spaces;
- no disposable names such as `copy`, `final2`, `(2)`;
- stable IDs independent of artwork changes;
- country/path consistency;
- transparent assets where appropriate;
- no arbitrary global dimension standard forced on unrelated source artwork;
- source provenance retained in the manifest layer.

Examples:

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

---

<p align="center">
  <img src="./assets/x1-picons-rights.svg" alt="X1 Picons Source and Rights Gate" width="100%" />
</p>

## Source / rights boundary

Finding a current logo online does **not** automatically prove redistribution rights.

X1 keeps these questions separate:

**Is this the correct/current artwork?**  
**Can X1 redistribute this asset?**

Source manifests exist so artwork can be audited with its source page, source URL, aliases, status, licensing note and trademark context.

Where redistribution permission is not clear, the correct state is **unresolved / not proven**, not an invented license assumption.

---

## Manifest validation

`tools/audit_manifests.py` validates the structured source manifests before synchronization and is intended to catch:

- malformed JSON;
- duplicate stable IDs;
- duplicate output paths;
- unsafe paths;
- invalid or unsupported source URLs;
- country/path mismatches;
- alias collisions;
- unsupported payload assumptions.

---

## Canonical metadata

`data/index.json` is designed to be the machine-readable catalogue authority once assets are materialized and validated.

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

Source manifests existing in Git do not by themselves prove that every corresponding asset is already materialized into the current index. Runtime/materialization state must be verified separately.

---

## Synchronization

The synchronization tooling audits manifests, downloads approved source assets, validates payloads, calculates hashes, refreshes catalogue metadata and produces operational reports.

See [`RUN_SYNC.md`](./RUN_SYNC.md) for the operational procedure.

---

## Relationship with X1 EPG

X1 Picons and X1 EPG can share stable canonical channel identities where appropriate:

```text
CHANNEL ID
   ├── EPG metadata / schedule
   └── PICON visual identity
```

Artwork can evolve without changing guide identity, and EPG source changes do not need to rename visual assets.

---

## Related X1 systems

- [X1 GitHub](https://github.com/x1-dotcom)
- [X1 EPG](https://github.com/x1-dotcom/x1epg)
- [X1 Stream Manager Community](https://github.com/x1-dotcom/X1-Stream-Manager-Community)

---

## Community

- Website — https://x1panelhq.com
- Forum — https://forum.x1panelhq.com
- Discord — https://discord.gg/vSSw6jHmw
- Telegram — https://t.me/+XkuQS_QuD6g4Nzc0

---

<p align="center">
  <strong>IDENTITY FIRST. ARTWORK SECOND. SOURCE TRACKED. RIGHTS EXPLICIT.</strong><br><br>
  <strong>X1 // SOFTWARE · SYSTEMS · OPERATIONS</strong><br><br>
  PUBLIC SOFTWARE. PRIVATE ENGINEERING. ONE X1 IDENTITY.<br><br>
  <strong>© X1Tech Solutions SA · All Rights Reserved</strong>
</p>
