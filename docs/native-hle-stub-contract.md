# Game-free native host contract

This is a portable C **host-only test interface**, not an implementation of Nintendo Horizon services or a Switch NRO loader. The numeric request IDs in `HLEContract.h` are deliberately unrelated to Horizon SVC identifiers.

`spk_host_dispatch` exposes a versioned, fixed-width ABI, a deterministic PING operation and explicit `NOT_IMPLEMENTED` for unknown requests. No unknown service returns success. Unit tests compile and execute this C source on a normal CI host, without any game binary.

| Request | ID | Argument | Reply |
|---|---|---|---|
| `SPK_HOST_PING` | 1 | any | `OK`, value = argument XOR `0x0A17A17A17A17A17` |
| `SPK_HOST_MONOTONIC_NANOS` | 2 | reserved, must be 0 | `OK`, value = host `CLOCK_MONOTONIC` in nanoseconds; non-zero argument → `INVALID_ARGUMENT`, value 0 |
| anything else | — | — | `NOT_IMPLEMENTED`, value 0 |

`SPKHostReply` is 16 bytes (`abi_version` at 0, `result` at 4, `value` at 8); `_Static_assert`s in `HLEContract.h` fail the build on any compiler that lays it out differently. Unit tests and the in-app probe bracket the clock reply between two direct `CLOCK_MONOTONIC` reads, which proves the clock source and the nanosecond unit.

`CLOCK_MONOTONIC` keeps counting while a Darwin device sleeps (Linux's does not). That is fine for host diagnostics, but it is not yet a Horizon system tick: the 2048 NRO reads `CNTVCT_EL0` directly, and any guest tick mapping (19.2 MHz counter, sleep behaviour) must be specified separately.

The same C source is compiled into the SwiftUI probe app; `HostContractProbe` runs every request above and the iOS Simulator E2E test asserts each PASS line. Still missing: a run on the physical iPad mini A17 Pro. Only after ABI and signed Mach-O verification should real Horizon service mapping be considered.

This component does not interpret or execute `.nro` bytes. It does not establish iPadOS compatibility with nxnative or any game.
