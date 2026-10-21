# Game-free native host contract

This is a portable C **host-only test interface**, not an implementation of Nintendo Horizon services or a Switch NRO loader. The numeric request IDs in `HLEContract.h` are deliberately unrelated to Horizon SVC identifiers.

`spk_host_dispatch` exposes a versioned, fixed-width ABI, a deterministic PING operation and explicit `NOT_IMPLEMENTED` for unknown requests. No unknown service returns success. Unit tests compile and execute this C source on a normal CI host, without any game binary.

Next: compile the same C source as part of the existing SwiftUI iOS app; add an in-app host smoke test, then test on the simulator and physical iPad. Only after ABI and signed Mach-O verification should real Horizon service mapping be considered.

This component does not interpret or execute `.nro` bytes. It does not establish iPadOS compatibility with nxnative or any game.
