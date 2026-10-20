# Existing Switch → Apple Native Port Projects

Source review: 2026-10-20. This document compares upstream developer claims and architecture; **we have not independently run these ports on iPad mini A17 Pro**.

| Project | Confirmed approach from README | Reuse potential | Caveat |
|---|---|---|---|
| [nxnative](https://github.com/seedds/nxnative) | ARM64 NSO rewriter, Horizon HLE, NVN→Metal, version-specific profiles | **Primary runtime** and profile pipeline | README lists iPad M1+; A17 Pro mini not explicitly supported |
| [d2r-mobile](https://github.com/d2r-mobile/d2r-mobile) | Native ARM64 + Metal, older-API iOS 18 builds, older GPU texture packs | **Prior-art for older A chips and API fallback** | Highly specialized to Diablo II |
| [Mush8](https://github.com/c22dev/mush8) | `nxpatch`, `nxhost`, linked game code on iOS, Metal, network modes | Compare port architecture / runtime tradeoffs | Designed for Mario Kart 8 Deluxe; README requires 6 GB+ RAM |
| [MacNativeGames](https://github.com/ly05010419/MacNativeGames) | TotK native Apple port, shader identifiers/shader prewarm, iOS 26+ | Shader pipeline and field diagnostics reference | Game-specific, not an off-the-shelf runtime for Shin chan |

## Material findings

1. nxnative credits d2r-mobile as the origin of its generic NSO rewriter, Horizon host, NVN/Metal layer, and iOS shell. Treating them as independent codebases to merge wholesale would duplicate related implementations.
2. d2r-mobile documents iOS 18 compatible builds and supplementary texture packs for older chips. This is a promising fallback *reference*, not proof that those mechanisms drop into nxnative unchanged.
3. Mush8 links rewritten game code into the iOS executable, similar in objective to nxnative's packaging approach. Its stated minimum is 6 GB RAM, so verify iPad mini A17 Pro memory compatibility rather than assuming a drop-in solution.
4. MacNativeGames advertises a shared shader identifier list and iPhone/iPad TotK experiments. Its profile and rendering optimizations are game-specific.

## Technical decision

**Keep nxnative as the single selected base for SwitchPortKit.** Do not combine separate HLE implementations prematurely. Research d2r-mobile's older API, graphics and CPU support, and adapt only isolated techniques after source-level comparison and license checks. For Shin chan, generating real game metadata and identifying the renderer remains on the critical path.

## Follow-up evidence requests

- Record upstream commit IDs and file-level diffs for selected older-API paths.
- Identify A17 Pro Metal 4 feature coverage and `-mcpu=apple-a18` generated instruction behavior using local, game-free tests.
- Obtain locally generated, legally sourced and sanitized Shin chan Survey metadata (title ID, Build IDs, engine, graphics API); no assets or keys in this repository.
- Demonstrate a tiny game-free host executable before claiming compatibility with any Switch title.

## Licensing

nxnative and d2r-mobile claim MIT in their top-level files, while Mush8 and MacNativeGames must be checked at the exact code/file level before copying anything. Keep all upstream copyright and third-party notices. No external code copied into this research document.
