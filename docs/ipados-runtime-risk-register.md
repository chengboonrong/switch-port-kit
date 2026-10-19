# nxnative iPadOS runtime risk register

Research date: 2026-10-20. **Source-based, not device-tested.** Target: iPad mini A17 Pro.

## Evidence from upstream

- [dm/ios/project.yml](https://github.com/seedds/nxnative/blob/main/dm/ios/project.yml) declares `deploymentTarget.iOS: 26.0` and explicitly notes use of Metal 4 (`MTL4CommandQueue`, etc.).
- The same file declares `TARGETED_DEVICE_FAMILY: "1,2"`, so the generated app targets iPhone and iPad. **This does not establish support for the iPad mini A17 Pro.**
- `OTHER_CFLAGS: $(inherited) -mcpu=apple-a18` is used because the host assembly needs LSE atomics. **Compiling for an A18 target does not imply that every emitted instruction is supported on A17 Pro.** Confirm disassembly and CPU feature requirements before changing flags.
- [README](https://github.com/seedds/nxnative/blob/main/README.md) documents iPhone A17 Pro+ and iPad M1+ as supported targets. The iPad mini A17 Pro is not explicitly claimed.
- [dm/gfx/tex/README.md](https://github.com/seedds/nxnative/blob/main/dm/gfx/tex/README.md) says compressed BC texture support is required and no BC decompression fallback exists.
- [dm/ios/tools/build_ipa.sh](https://github.com/seedds/nxnative/blob/main/dm/ios/tools/build_ipa.sh) embeds the rewritten game modules and shader libraries in an unsigned IPA; signing is a separate step.

## Risk priorities

| Risk | Severity | Verification |
|---|---|---|
| Metal 4 API availability on iPad mini A17 Pro / target OS | Blocker until checked | Audit API and Apple feature availability; do not equate iPadOS 26 with every feature |
| A18-specific CPU instruction emission | Blocker until checked | Produce compiler/disassembler probe; inspect host assembly and `-mcpu` usage |
| iPad target support inferred from bundle settings | High | Identify actual runtime device checks and allocation assumptions |
| BC texture read, upload and sampling | High | BC1/BC3 sampling test on physical A17 Pro; extend to BC7 |
| Per-game RAM and GPU footprint | High | Inspect measured title profile, not guesses |
| Code-signing and executable module embedding | High | Verify actual signed artifact and launch in iPadOS |

## Desktop-only audit acceptance criteria

1. Pin upstream commit SHA and enumerate Metal4 symbols used in `dm/gfx`.
2. Identify architecture-sensitive A18-only operations, compiler flags and custom assembly.
3. Create a minimal freestanding C/assembly compile check for A17 compatibility **without** claiming runtime safety.
4. Ensure diagnostic reports and issue templates contain no ROMs, keys, local paths or shader assets.
5. Only then propose specific upstream compatibility changes behind an opt-in flag.

No automatic downgrade from Metal 4 to Metal 3 should be attempted without a complete API dependency audit. No hardware support claim without device evidence.
