# nxnative → iPad mini A17 Pro: desktop-only audit

Status: **desktop/source audit only**. No nxnative code was built or run, and nothing has been tested on a physical device.

## Sources reviewed (2026-11-01)

All files are at upstream commit [`dad38db62ef549404b617a73aa18d31aa8117c8e`](https://github.com/seedds/nxnative/commit/dad38db62ef549404b617a73aa18d31aa8117c8e). This replaces the 2026-10-20 audit, which pinned file blobs rather than a commit.

- [README](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/README.md) and [LICENSE](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/LICENSE)
- [Development guide](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/docs/development.md)
- [Rendering reference](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/docs/reference/rendering.md)
- [Texture design notes](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/dm/gfx/tex/README.md)
- [Third-party licenses](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/dm/third_party/README.md)
- [iOS app start-up](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/dm/ios/Sources/main.m) and [iOS project](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/dm/ios/project.yml)
- [IPA builder](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/dm/ios/tools/build_ipa.sh)
- [NSP builder](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/scripts/build_ipa_from_nsp.py)

Upstream changes daily and has no tagged releases, so re-pin before relying on this audit. Repository-wide device-gate searches used GitHub code search, which covers the default branch; finding nothing there is not proof of absence.

## Confirmed architecture

- `dm/tools/patch_nso.py` rewrites game ARM64 modules; `dm/host` provides Horizon HLE.
- `dm/gfx` handles NVN-to-Metal. Games that render with Vulkan (Hades) or OpenGL (Digimon Story Cyber Sleuth) use their own layers on Metal, `dm/gfx/vk` and `dm/gfx/gl`.
- `dm/ios/tools/build_ipa.sh` builds an unsigned IPA for iPhone and iPad: the rewritten code is in the executable, with shader libraries and RomFS in the bundle. Signing happens later, in Xcode or a sideloading tool. By default the IPA requests the Increased Memory Limit entitlement.
- The iOS deployment target is 26.0 because graphics replay uses Metal 4. Builds need macOS 26.6+, Xcode 27.2 and Python 3.12+.
- The development guide says the iOS Simulator cannot run the game's code, so simulator results say nothing about a game on this device.

## Device support

The README lists iOS/iPadOS **26+** on iPhone 15 Pro or newer (A17 Pro or later) and iPads with **M1** or later. An A17 Pro iPad mini is **not listed**.

The listed split comes from BC textures, not from a device list:
- `front_ios_device_check` in `dm/ios/Sources/main.m` runs when Play is pressed and refuses to start only if `MTLDevice.supportsBCTextureCompression` is false; `mtl_init` repeats the check on the other routes. It does not check the device model.
- The refusal message names the supported devices, but the decision uses only that GPU property. Upstream's comment there gives A16 and older as the GPUs without BC.
- `dm/ios/project.yml` targets iPhone and iPad, and code search finds no `UIRequiredDeviceCapabilities`. The one `hw.machine` read found, in `dm/host/save_sync.c`, only labels which device a save came from.

So this check would admit the iPad mini A17 Pro if its GPU reports BC support. That is unmeasured, and passing this check says nothing about whether a game then runs.

Upstream requires BC support and has no decompression fallback, so BC textures are created and uploaded as BC. A successful compressed texture allocation does **not** prove uploads, sampling or correct colors.

Offline pipeline archives are per GPU architecture. The host opens the file named after `MTLDevice.architecture`. The game profile's `pso_gpu` picks which GPU the app carries an archive for, falling back to the A19 family (`applegpu_g18p`) for a game with `pso_mtl4` on; `--gpu` adds others. With no archive for the device's GPU, the device runs its own prebuild, so A17 Pro would pay that cost unless one is built for its architecture, which this probe does not yet report.

The earlier note about narrower-screen support in `dm/host/dm_uiscreen.h` is withdrawn: that file no longer exists at this commit, and iPad mini layout remains untested.

## Licensing

Top-level nxnative license is MIT. The copyright line changed from `jhaizhou` (2026-10-20 audit) to `seedds`; the license text did not. Bundled third-party sources keep their own licenses:

| Source | License |
|---|---|
| NVIDIA FLIP, libvpx | BSD-3-Clause (libvpx also has a patent grant in `PATENTS`) |
| stb_vorbis | MIT or public domain |
| Ryujinx shader library | MIT (`Spv.Generator` has its own license file) |
| Vulkan headers | Apache-2.0 or MIT |
| deko3d-derived layout code in `dm/gfx/nvn/nvn_tex.c` | zlib |
| `dm/gfx/nvn/include/nvn.h`, code adapted from MacNativeGames | MIT |

Keep the relevant notices and check all transitive and bundled sources before importing. This repo currently **does not import upstream code**.

## Security and reproducibility

`scripts/build_ipa_from_nsp.py` no longer ships developer-specific paths: `NSP_DIR` and `PROD_KEYS` default to empty and are asked for at run time. The rule here is unchanged: our tools must not inspect, upload, log or collect `prod.keys`, game dumps, NSPs or copyrighted content. Prefer CLI options or ignored local configuration, and keep game ROMs and IPA packages out of CI.

## Unresolved blockers / verification matrix

| Question | State | Next evidence |
|---|---|---|
| A17 Pro iPad GPU reports BC compression | Unverified on target | Run Metal probe |
| BC1 / BC3 / BC7 allocations | Unverified | Run Metal probe |
| Correct compressed texture sampling | BC1/BC3 readback in probe, unverified on target; BC7 not tested | Run Metal probe; add BC7 |
| Reason for the iPad M1+ wording | Answered: the start-up gate is the BC capability, not a device list | Re-check at each re-pin |
| A17 Pro GPU architecture name for pipeline archives | Unknown; probe does not report it | Add `MTLDevice.architecture` to the probe report |
| Runtime executable/codesigning constraints | Unverified on iPad mini | Audit embed/entitlements, then test |
| GPU and RAM headroom for selected title | Unknown | Per-title footprint + physical run |
| Representative NVN title | Undecided | Prefer upstream supported non-Vulkan title |
| Third-party obligations for copied code | Audit required at import time | License manifest |

## Recommendation

Keep the first deliverable a standalone Metal probe, and run it on the physical iPad mini A17 Pro. Treat the BC result as the first go/no-go. Do not patch or bypass upstream's device check. Do not attempt a commercial-title conversion until the runtime and GPU blockers have recorded evidence.
