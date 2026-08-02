# TRIZ engine provenance

This engine contains original operational guidance plus a small set of data
files derived from the MIT-licensed
[`jenson500/triz-prompt-engineering`](https://github.com/jenson500/triz-prompt-engineering)
project, pinned at commit
`a3812e200711ad443c3db5fc57ebc05fe0c5c91d`.

The full upstream repository, prompt collection, PDFs, and spreadsheets are not
vendored. The source files consulted and the concepts retained are documented
in `../../../docs/maintainers/triz-engine/source-map.md`.

## Retained data checksums

SHA-256 checksums identify the exact derived runtime fixtures shipped here:

| Relative file | SHA-256 |
|---|---|
| `scripts/data/contradiction_matrix.csv` | `b941d25b3400934df868968cd62a6c1b1bf536b83d349c593b1aeef2b1b062ce` |
| `scripts/data/parameters_39.csv` | `bc69941f88dff35618f6e57d2e37a8ce1250d48065d216fc84014dde0e7e92ed` |
| `scripts/data/inventive_principles.csv` | `cedd87a7bb4e54a4a730d5edc9a24f4bfb80ae5f56470b551255b6e8420b387d` |
| `scripts/data/scientific_effects.json` | `bbb36c0a04d56d0805f3e2c605cd50fae86ea53aa0bd66d3a3ce8cc68a9622d1` |
| `scripts/data/standard_solutions_76.json` | `0ff7828ee71a6ddbcf49af8e80b2cba9ba980464d6333fc1c89959b1cbc74a6b` |

Upstream README Git blob: `1d7e0ba0`. Upstream license Git blob:
`3129c1f3`. The pin above is authoritative; hashes are recorded to make source
drift visible, not to claim byte-for-byte copying of every derived fixture.

## Upstream license

The upstream license is preserved in `UPSTREAM_LICENSE` beside this file. The
repository's own code and documentation are licensed under the root MIT
license.
