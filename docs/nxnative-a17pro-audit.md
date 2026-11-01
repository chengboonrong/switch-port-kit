# nxnative → iPad mini A17 Pro: desktop-only audit

Status: **desktop/source audit only**. No nxnative code was built or run, and this project has tested nothing on a physical device.

## Sources reviewed (2026-11-01)

All files are at upstream commit [`dad38db62ef549404b617a73aa18d31aa8117c8e`](https://github.com/seedds/nxnative/commit/dad38db62ef549404b617a73aa18d31aa8117c8e). This replaces the 2026-10-20 audit, which pinned file blobs rather than a commit.

- [README](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/README.md) and [LICENSE](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/LICENSE)
- [Development guide](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/docs/development.md)
- [Rendering reference](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/docs/reference/rendering.md)
- [Texture design notes](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/dm/gfx/tex/README.md)
- [Third-party licenses](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/dm/third_party/README.md)
- [iOS app start-up](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/dm/ios/Sources/main.m), [launcher](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/dm/ios/Sources/front_ios.m) and [iOS project](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/dm/ios/project.yml)
- [Save sync](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/dm/host/save_sync.c), and the device checks in [`nvn_mtl.m`](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/dm/gfx/nvn/nvn_mtl.m)
- [IPA builder](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/dm/ios/tools/build_ipa.sh)
- [NSP builder](https://github.com/seedds/nxnative/blob/dad38db62ef549404b617a73aa18d31aa8117c8e/scripts/build_ipa_from_nsp.py)
- [Upstream issue #626](https://github.com/seedds/nxnative/issues/626), read on 2026-11-01; issues are not pinned to a commit

Upstream changes daily and has no tagged releases, so re-pin before relying on this audit. Repository-wide device-gate searches used GitHub code search, which covers the default branch; finding nothing there is not proof of absence. `front_ios.m` and `nvn_mtl.m`, which run the device checks, were also searched directly.

## Confirmed architecture

- `dm/tools/patch_nso.py` rewrites game ARM64 modules; `dm/host` provides Horizon HLE.
- `dm/gfx` handles NVN-to-Metal. Games that render with Vulkan (Hades) or OpenGL (Digimon Story Cyber Sleuth) use their own layers on Metal, `dm/gfx/vk` and `dm/gfx/gl`.
- `dm/ios/tools/build_ipa.sh` builds an unsigned IPA for iPhone and iPad: the rewritten code is in the executable, with shader libraries and, by default, RomFS in the bundle. The executable is ad-hoc signed only to carry entitlements, by default Increased Memory Limit. Real signing happens later, in Xcode or an install tool.
- The iOS deployment target is 26.0 because graphics replay uses Metal 4. Builds need macOS 26.6+, Xcode 27.2 and Python 3.12+.
- The development guide says the iOS Simulator cannot run the game's code, so simulator results say nothing about a game on this device.

## Device support

The README lists iOS/iPadOS **26+** on iPhone 15 Pro or newer (A17 Pro or later) and iPads with **M1** or later. An A17 Pro iPad mini is **not listed**. The README's game list is "tested on Mac or iPhone", so the M1 wording is a requirement, not a tested-iPad claim.

The listed split comes from BC textures, not from a device list:
- `front_ios_device_check` in `dm/ios/Sources/main.m` runs when Play is pressed, or at once in an app without a launcher, and refuses to start only if `MTLDevice.supportsBCTextureCompression` is false. It does not check the device model.
- `mtl_init` in `nvn_mtl.m` stops the other routes the same way. It also requires unified memory, and the NVN layer needs the Metal 4 GPU family; the probe reports neither.
- The refusal message names the supported devices, but the decision uses only that GPU property. Upstream's comment there gives A16 and older as the GPUs without BC.
- `dm/ios/project.yml` targets iPhone and iPad, and code search finds no `UIRequiredDeviceCapabilities`. The one `hw.machine` read found, in `dm/host/save_sync.c`, only labels which device a save came from.

So these checks would admit the iPad mini A17 Pro if its GPU reports those capabilities. This project has not measured that, and passing them says nothing about whether a game then runs.

The iOS target also compiles with `-mcpu=apple-a18`, a newer chip than A17 Pro. Upstream's comment gives LSE atomics in the host assembly as the reason, and A17 Pro iPhones are listed as supported, but these sources do not show what else the flag lets the compiler emit. `docs/cpu-compat-audit.md` already marks this flag as needing a toolchain and binary disassembly audit.

Upstream requires BC support and has no decompression fallback, so BC textures are created and uploaded as BC (the texture notes' title and item 3 still mention decompression; their later section and the rendering reference say that path is gone). A successful compressed texture allocation does **not** prove uploads, sampling or correct colors.

Offline pipeline archives matter only on the Metal 4 path, which iOS turns on for a game with `pso_mtl4 on` or `DM_PSO_MTL4=1`. An archive is per GPU architecture and per OS major version: the host opens the file named after `MTLDevice.architecture`, and a device opens only an archive made for its own major version. The game profile's `pso_gpu` picks the architectures, falling back to the A19 family (`applegpu_g18p`); `--gpu` replaces that list. With no usable archive the device builds the bases itself on first start, so on this path an A17 Pro iPad would pay that cost unless an archive is built for its architecture and OS. The probe does not yet report the architecture.

The earlier note about narrower-screen support in `dm/host/dm_uiscreen.h` is withdrawn: that file no longer exists at this commit, and iPad mini layout remains untested.

## Third-party report on this device

[Upstream issue #626](https://github.com/seedds/nxnative/issues/626) reports DRAGON QUEST XI S 1.0.4 on an iPad mini 7 (A17 Pro, `iPad16,1`, iPadOS 26.7.1). With the Frame buffering setting off, the reporter entered the game and the log reached more than 5,400 frames with no GPU submission errors. With it on, the game froze at startup. Upstream's owner traced that to a residency bug and fixed it; the rendering reference records the fix as not checked on the iPad.

This is not evidence from this project, and it does not make the device supported:
- **Build:** made on 2026-10-29 with the reporter's local changes, so it is not this audit's commit.
- **Scope:** the reporter calls it one working run, not a stability or artifact-free claim, and does not assume the device is validated upstream. It covers one game.
- **BC:** upstream says a GPU without BC aborts at the first BC texture, so the run suggests this iPad's GPU has BC. That is an inference from someone else's log, not a measurement, so the matrix row stays open.

## Licensing

Top-level nxnative license is MIT. The copyright line changed from `jhaizhou` (2026-10-20 audit) to `seedds`; the license text did not. The README says nxnative started from d2r-mobile (MIT), and the tree has no separate license file for it, so trace that notice before importing anything derived from it. Third-party code in the tree keeps its own license:

| Source | License |
|---|---|
| NVIDIA FLIP, libvpx | BSD-3-Clause (libvpx also has a patent grant in `PATENTS`) |
| stb_vorbis | MIT or public domain |
| Ryujinx shader library, with local changes | MIT (`Spv.Generator` has its own license file) |
| Vulkan headers | Apache-2.0 or MIT |
| Layout code in `dm/gfx/nvn/nvn_tex.c`, from deko3d | zlib |
| `dm/gfx/nvn/include/nvn.h` | MIT (author in the file header) |
| Code adapted from MacNativeGames in `dm/gfx/nvn/nvn_mtl.m` and `dm/gfx/tools/dmsh_xlate/Program.cs` | MIT |
| `stb_image.h`, `stb_image_write.h`, `tinyexr.h` in `dm/third_party/flip/tool/` | Notices in the files; not read |
| Vendored `spirv-cross` in `dm/gfx/tools/spirv_cross_bin/` | Own `LICENSE` and `LICENSES/` (Apache-2.0, CC-BY-4.0, MIT, Khronos); not read. Not in upstream's third-party README |

Keep the relevant notices and check all transitive and bundled sources before importing. This repo currently **does not import upstream code**.

## Security and reproducibility

`scripts/build_ipa_from_nsp.py` no longer ships developer-specific paths: `NSP_DIR` and `PROD_KEYS` default to empty and are asked for at run time. The rule here is unchanged: our tools must not inspect, upload, log or collect `prod.keys`, game dumps, NSPs or copyrighted content. Prefer CLI options or ignored local configuration, and keep game ROMs and IPA packages out of CI.

## Unresolved blockers / verification matrix

| Question | State | Next evidence |
|---|---|---|
| A17 Pro iPad GPU reports BC compression | Unverified by this project; issue #626 suggests yes | Run Metal probe |
| BC1 / BC3 / BC7 allocations | Unverified | Run Metal probe |
| Correct compressed texture sampling | BC1/BC3 readback in probe, unverified on target; BC7 not tested | Run Metal probe; add BC7 |
| Reason for the iPad M1+ wording | Answered: the BC capability, in `main.m` and `mtl_init`; no device-model check found | Re-check at each re-pin |
| A17 Pro iPad Metal 4 family and GPU architecture name | Unverified; probe reports neither | Add both to the probe report |
| `-mcpu=apple-a18` build on A17 Pro | Unknown; no binary audit | Toolchain and disassembly audit before import |
| Runtime executable/codesigning constraints | Unverified on iPad mini | Audit embed/entitlements, then test |
| GPU and RAM headroom for selected title | Unknown | Per-title footprint + physical run |
| Representative NVN title | Undecided; issue #626 covers one title on this device | Prefer upstream supported non-Vulkan title |
| Third-party obligations for copied code | Audit required at import time | License manifest |

## Recommendation

Keep the first deliverable a standalone Metal probe, and run it on the physical iPad mini A17 Pro. Issue #626 raises the odds of a pass, but this project needs its own measurement. Treat the BC result as the first go/no-go. Do not patch or bypass upstream's device check. Do not attempt a commercial-title conversion until the runtime and GPU blockers have recorded evidence.
