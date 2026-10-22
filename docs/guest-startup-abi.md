# 2048 NRO guest startup ABI

What the host must provide for the user-supplied `2048.nro` to get from its entry point to `main`. Everything below was measured from that file with the repository tools, or read from libnx source, and checked against the binary. **Nothing here has been executed.** Offsets are relative to the start of the NRO image (text starts at file offset 0). No NRO bytes are committed.

Reference source: [switchbrew/libnx](https://github.com/switchbrew/libnx) at `b156b47` (2026-10-19). The exact libnx version 2048 was built with is unknown. Every libnx claim used here was matched against 2048's own code, as listed in each section.

## Image layout

| Range | Contents | Permission after startup |
|---|---|---|
| `0x000000–0x02b000` | text (NRO header at `0x10`, MOD0 at `0xf0`) | R-X |
| `0x02b000–0x143000` | rodata | R |
| `0x143000–0x144000` | RELRO (MOD0 `LNY1`): `.dynamic` at `0x1434e0` and the GOT `0x143630–0x143a00` (`LNY0`) | RW during relocation, then R |
| `0x144000–0x148000` | data | RW |
| `0x147100–0x14ba68` | BSS (MOD0; starts inside the last data page), header BSS size `0x4000` → image ends at `0x14c000` | RW, zeroed |

The `eh_frame_hdr` range is empty (start = end = `0x13b62c`).

## Entry contract

The entry is libnx `switch_crt0.s`: `b 0x80`, then at `0x80` the same instruction sequence as libnx, instruction for instruction.

| Register | Value for an NRO launch |
|---|---|
| `x0` | guest address of the loader config list (below); must be non-zero |
| `x1` | `0xFFFFFFFFFFFFFFFF` |
| `x30` | loader return address. libnx keeps it and, on exit, restores `sp` and branches there with `w0` = result code |
| `sp` | top of the main-thread stack, 16-byte aligned; saved to `__stack_top` |

crt0 dispatch: `x0 != 0 && x1 != UINT64_MAX` enters `__libnx_exception_entry` (`0xf51c`). `x0 == 0` is the NSO path, with `x1` = main thread handle. The homebrew path above is the only one this spec covers.

## Startup sequence

crt0 calls `__nx_dynamic` and then `__libnx_init` (`0xd0f0`). `__libnx_init` makes the same 8 calls, in the same order, as libnx `init.c`; crt0 then branches to `main` (`0x540`).

| # | Offset | libnx function | Direct-edge SVC candidates | Host obligation |
|---|---|---|---|---|
| 0 | `0xccc0` | `__nx_dynamic` | `0x2` SetMemoryPermission, `0x3` SetMemoryAttribute, `0x26` Break | After the guest applies its own 521 RELR relocations, make `0x143000–0x144000` read-only (failure aborts), then accept the permission-lock attribute |
| 1 | `0x68d0` | `envSetup` | none | Valid config list in `x0` |
| 2 | `0xd5a0` | `newlibSetup` | `0x26` | Main thread handle (calls `envGetMainThreadHandle`); guest TLS block |
| 3 | `0x7730` | `virtmemSetup` | `0x29` GetInfo, `0x5` UnmapMemory, `0x1a` ArbitrateLock, `0x26` | Address-space region info |
| 4 | `0xced0` | `__libnx_initheap` | `0x1` SetHeapSize, `0x29` GetInfo, `0x26` | Passing `OverrideHeap` skips `0x1` and both `0x29` queries (branch at `0xcee4`) |
| 5 | `0xfca0` | `__libnx_init_thread` | `0x6` QueryMemory, `0x1a`, `0x1b` ArbitrateUnlock, `0x26` | Main thread handle; queries its own stack mapping |
| 6 | `0xc980` | `argvSetup` | `0x6`, `0x1a`, `0x26` | — |
| 7 | `0xcfb0` | `__appInit` | `0x6 0xb 0x13 0x14 0x16 0x17 0x18 0x1a 0x1b 0x1c 0x1d 0x1f 0x21 0x26 0x29 0x52` | Horizon services over IPC (below) |
| 8 | `0x21ca0` | `__libc_init_array` (tail call) | none; 4 indirect | Static constructors run through `blr` |

The SVC columns come from `analyze_entry(nro, start=<offset>)` in `tools/nro_direct_cfg.py`. That analysis follows only direct branches and stops at `UDF`; it does not follow `blr`, so calls through function pointers are missing and the sets are candidates, not traces. SVC names are from libnx `svc.s`.

`__appInit` is libnx's default. Its abort codes are Module 345 with `InitFail_SM`, `InitFail_AM`, `InitFail_HID`, `InitFail_Time` and `InitFail_FS`, and it initializes, in order:
- **`sm`:** required.
- **`set:sys`:** only if no host version is known; failure is tolerated.
- **`applet`:** required.
- **`hid`:** required unless the applet type is `None`.
- **`time`:** required.
- **`fs`:** required.
- **Others:** it then mounts `sdmc`, and runs the window init and `userAppInit` if linked.

This IPC layer is the next blocker.

## Loader config list

libnx `ConfigEntry`: `u32 key`, `u32 flags`, `u64 value[2]`, 24 bytes. 2048's `envSetup` steps through the list `0x18` bytes at a time until key 0. Its jump table covers keys 1–17 (`cmp w1, #0x10` after `key - 1`), and it contains the `HosVersion` `ATMOSPHR` check, so it is a libnx at least as new as key 17 (`SyscallAvailableHint2`). An unhandled key with flag bit 0 (mandatory) set exits to the loader with Module 346 (HomebrewAbi), description `100 + key`. `END_OF_LIST` carries an optional loader-info string pointer and size.

`spk_guest_config_build` (`apps/A17ProMetalProbe/GuestStartup.c`) emits:

| Key | Entry | Why |
|---|---|---|
| 1 | `MainThreadHandle` | Required. `envGetMainThreadHandle` (`0x6ae0`) aborts with `HandleTooEarly` on handle 0; it is called in steps 2 and 5 |
| 3 | `OverrideHeap` (optional) | Host-allocated heap; removes `svcSetHeapSize` and two `svcGetInfo` calls |
| 0 | `EndOfList` | No loader info |

Flags are always 0, so an older libnx that lacks a key ignores it instead of exiting. The builder rejects handle 0, a heap address without a size (or the reverse), NULL pointers and a buffer that is too small; in the last case it reports the required count.

Deliberately not emitted (open host-policy decisions):
- **`SyscallAvailableHint` / `SyscallAvailableHint2` (6, 17):** in libnx only `jit.c` reads them, so leaving them out claims no SVCs.
- **`AppletType` (7):** without it libnx uses `AppletType_Default`, the application path. `AppletType_None` would skip applet-dependent init, including `hid`, but whether 2048's display path then works is unmeasured.
- **`HosVersion` (16):** without it `__appInit` queries `set:sys` for the firmware version. Sending one avoids that IPC but means choosing a version to report.
- **`Argv` (5) and the rest:** not needed to reach `main`.

## ABI translation items found on this path

- **`TPIDRRO_EL0`:** libnx keeps its 0x200-byte thread-local block there; thread vars live at `+0x1e0` with magic `0x21545624` (read at `0xd160`). Darwin uses `TPIDRRO_EL0` for its own per-thread data and EL0 cannot write it, so guest reads must be rewritten to a host-managed per-thread pointer.
- **x18:** reserved by Apple; see `docs/nro-x18-abi-audit.md`.
- **SVCs:** none of the candidates above can be issued on iPadOS. Each must become a call into the host, with the result codes the guest checks.

## Not established

- That any of this code runs: no guest instruction has been executed, on simulator or device.
- Which `blr` targets are reached during startup.
- The guest stack size, TLS block allocation, and the main thread handle value the host should pass.
- Any of the IPC services listed for `__appInit`.
