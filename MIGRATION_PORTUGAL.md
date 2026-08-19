# Portugal legacy migration

This document tracks the controlled migration of historical root PNGs to the structured X1 picon library.

## Rule

A legacy file is **not** removed merely because a manifest exists. Removal requires all of the following:

1. the modern asset exists under `countries/pt/`;
2. the modern asset is present in `data/index.json`;
3. the indexed SHA-256 matches the real asset;
4. X1 consumers resolve the modern ID/path correctly;
5. there is no unresolved visual/semantic ambiguity.

Machine-readable authority: `data/legacy-migration-pt.json`.

## Direct migration candidates

| Legacy root file | Modern ID | Modern path | Current state |
|---|---|---|---|
| `rtp1.png` | `rtp-1` | `countries/pt/rtp-1.svg` | WAIT_MATERIALIZATION |
| `rtp2.png` | `rtp-2` | `countries/pt/rtp-2.svg` | WAIT_MATERIALIZATION |
| `rtp3 (2).png` | `rtp-noticias` | `countries/pt/rtp-noticias.svg` | WAIT_MATERIALIZATION |
| `rtpafrica.png` | `rtp-africa` | `countries/pt/rtp-africa.svg` | WAIT_MATERIALIZATION |
| `memoria.png` | `rtp-memoria` | `countries/pt/rtp-memoria.svg` | WAIT_MATERIALIZATION |
| `rtpacores.png` | `rtp-acores` | `countries/pt/rtp-acores.svg` | WAIT_MATERIALIZATION |
| `madeira.png` | `rtp-madeira` | `countries/pt/rtp-madeira.svg` | WAIT_MATERIALIZATION |
| `sicnoticias.png` | `sic-noticias` | `countries/pt/sic-noticias.svg` | WAIT_MATERIALIZATION |
| `sicmulher.png` | `sic-mulher` | `countries/pt/sic-mulher.svg` | WAIT_MATERIALIZATION |
| `siccaras.png` | `sic-caras` | `countries/pt/sic-caras.png` | WAIT_MATERIALIZATION |
| `cnnportugal.png` | `cnn-portugal` | `countries/pt/cnn-portugal.svg` | WAIT_MATERIALIZATION |
| `sporttv+.png` | `sport-tv-plus` | `countries/pt/sport-tv-plus.svg` | WAIT_MATERIALIZATION |
| `sporttv1.png` | `sport-tv-1` | `countries/pt/sport-tv-1.svg` | WAIT_MATERIALIZATION |
| `sporttv2.png` | `sport-tv-2` | `countries/pt/sport-tv-2.svg` | WAIT_MATERIALIZATION |
| `sporttv3.png` | `sport-tv-3` | `countries/pt/sport-tv-3.svg` | WAIT_MATERIALIZATION |
| `sporttv_4.png` | `sport-tv-4` | `countries/pt/sport-tv-4.svg` | WAIT_MATERIALIZATION |
| `sporttv5_.png` | `sport-tv-5` | `countries/pt/sport-tv-5.svg` | WAIT_MATERIALIZATION |
| `sporttv6.png` | `sport-tv-6` | `countries/pt/sport-tv-6.svg` | WAIT_MATERIALIZATION |
| `tvi.png` | `tvi` | `countries/pt/tvi.png` | WAIT_MATERIALIZATION |
| `tvificcao.png` | `tvi-ficcao` | `countries/pt/tvi-ficcao.png` | WAIT_MATERIALIZATION |

`rtp3 (2).png` is intentionally mapped to `rtp-noticias`: the modern manifest keeps `RTP3` and `RTP 3` as aliases for compatibility.

## Legacy files without an approved modern replacement

Do **not** delete these yet. Examples include `sic.png`, `sicradical.png` and `cmtv.png`. They remain compatibility assets until a current redistributable source is approved and materialized.

## Visual review queue

Filename similarity is not enough to delete a file. The following known pairs differ at the byte level and remain under review:

- `axnmovies.png` / `axnmovies (2).png`
- `axnwhite.png` / `axnwhite (2).png`
- `odisseia (1).png` / `odisseia (2).png`
- `tvcineedition.png` / `tvcineedition (2).png`
- `tvcineemotion.png` / `tvcineemotion (2).png`

## State transitions

`WAIT_MATERIALIZATION` → `READY_FOR_COMPAT_TEST` → `READY_FOR_REMOVAL`

Any ambiguity moves an entry to `NEEDS_VISUAL_REVIEW`. A file with no approved replacement remains `NO_MODERN_EQUIVALENT`.

No automatic deletion is permitted from this table.
