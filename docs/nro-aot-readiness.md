# NRO → iPadOS signed AOT readiness gate

`python3 -m tools.nro_aot_readiness /private/2048.nro`

Aggregates existing RELR, candidate CFG, SVC/system-register and partial x18 scans into a **fail-closed** list of engineering blockers. The report is metadata only. The NRO stays on the local machine. No source code or game bytes are uploaded.

The gate deliberately always marks `ready_to_build_ipa: false` until a real AOT Mach-O generator, libnx/Horizon bridge, graphics/input implementation, and hardware verification exist. A zero count from any static scanner is **not** proof of safety.

The most important next executable milestone is a **game-free signed Mach-O host** that demonstrates stable guest ABI translation and deterministic Horizon stub behavior on a physical A17 Pro, before trying the 2048 binary. A runtime NRO loader that maps executable guest pages is not assumed to be acceptable under standard iPadOS code-signing policy.
