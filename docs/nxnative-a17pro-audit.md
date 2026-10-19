# nxnative → iPad mini A17 Pro: desktop-only audit

Status: **desktop/source audit only**. No Xcode build or physical-device test has occurred.

## Sources reviewed (2026-10-20)

- [Upstream README](https://github.com/seedds/nxnative/blob/main/README.md), blob `997065ad6a4d80c15ec7940b6ce464d24508cca7`
- [Upstream LICENSE](https://github.com/seedds/nxnative/blob/main/LICENSE), blob `e98c7620fff706c032c62d120eef265c4d9ee408`
- [Development guide](https://github.com/seedds/nxnative/blob/main/docs/development.md), blob `e34492ce77d2067f8fbff79c20a9da0a6dc0167b`
- [Texture design notes](https://github.com/seedds/nxnative/blob/main/dm/gfx/tex/README.md)
- [Third-party licenses](https://github.com/seedds/nxnative/blob/main/dm/third_party/README.md)
- [IPA builder](https://github.com/seedds/nxnative/blob/main/dm/ios/tools/build_ipa.sh)
- [NSP builder](https://github.com/seedds/nxnative/blob/main/scripts/build_ipa_from_nsp.py), blob `4414e111f2422f48b020f19e11ca9b8d6b69c481`

The above pinned **blob IDs** reflect inspected file content, not a validated single repository commit. Pin a full upstream commit SHA before reproducing the audit.

## Confirmed architecture

- `dm/tools/patch_nso.py` rewrites game ARM64 modules; `dm/host` provides Horizon HLE.
- `dm/gfx` handles NVN-to-Metal; a separate Vulkan route is used for **Hades**.
- `dm/ios/tools/build_ipa.sh` embeds rewritten modules, shader libraries, and RomFS into an unsigned IPA. Signing happens later.
- Upstream describes iOS/iPadOS **26+**, iPhone **A17 Pro+**, and iPad **M1+** as supported device categories. An A17 Pro iPad mini is **not listed as supported**. No direct claim of an iPad-specific runtime check can yet be made from README alone.
- Upstream's texture documentation requires `MTLDevice.supportsBCTextureCompression` and states there is no BC decompression fallback. Probe the actual property on physical hardware; a successful compressed texture allocation does **not** prove uploads, sampling, or correct colors.
- Device presentation already has narrower-screen layout support in `dm/host/dm_uiscreen.h`, but iPad mini integration remains untested.

## Licensing

Top-level nxnative license is MIT (copyright 2026 jhaizhou). The bundled third-party sources have their own licenses including BSD-3-Clause, Apache-2.0/MIT, MIT, and zlib. Keep relevant notices and check all transitive/bundled sources before importing. This repo currently **does not import upstream code**.

## Security and reproducibility

`scripts/build_ipa_from_nsp.py` checked-in defaults include developer-specific absolute paths to the NSP directory and `prod.keys`. **Paths are not keys**, but should never be copied into this repository. Our tools must not inspect, upload, log, or collect `prod.keys`, game dumps, NSPs, or copyrighted content. Prefer CLI options or ignored local configuration. Avoid adding game ROMs or IPA packages to CI.

## Unresolved blockers / verification matrix

| Question | State | Next evidence |
|---|---|---|
| A17 Pro iPad GPU reports BC compression | Unverified on target | Run Metal probe |
| BC1 / BC3 / BC7 allocations | Unverified | Run Metal probe |
| Correct compressed texture sampling | Not implemented in probe | Test patterns + readback |
| Existing iPad M1+ wording due to actual gate | Unknown | Locate exact gate in app host/build scripts |
| Runtime executable/codesigning constraints | Unverified on iPad mini | Audit embed/entitlements, then test |
| GPU and RAM headroom for selected title | Unknown | Per-title footprint + physical run |
| Representative NVN title | Undecided | Prefer upstream supported non-Vulkan title |
| Third-party obligations for copied code | Audit required at import time | License manifest |

## Recommendation

Keep the first deliverable a standalone Metal probe. After capability confirmation, investigate the iPad M1 requirement at **source level** (not by bypassing the device whitelist). Do not attempt a commercial-title conversion until the runtime and GPU blockers have recorded evidence.
