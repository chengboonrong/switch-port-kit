# A17ProMetalProbe UI test contract

The following SwiftUI accessibility identifiers are stable and intended for native UI and TesterArmy e2e smoke tests:

| Identifier | Element | Expected behavior |
|---|---|---|
| `probe.run` | Button | Starts diagnostic capture |
| `probe.result` | Text | Initially explains how to start; then displays a report or an error |
| `probe.share` | ShareLink | Opens the platform share experience for the current report |

## Simulator assertions

- Launch app, assert `probe.run` and `probe.result` exist.
- Tap `probe.run`; assert result changes from the initial instruction and reports Metal details **or** `ERROR: Metal device unavailable.`
- Assert `probe.share` exists.

## Explicit non-goals

A simulator test cannot establish A17 Pro compressed texture support, NVN rendering, Switch binary execution, or frame-rate performance. Do not assert `apple9_family: true` in the simulator. TesterArmy e2e package API/configuration must be verified and pinned before writing or enabling a CI workflow. No game files, keys, or private hardware reports belong in CI.

Status: test contract authored; **not** run on Xcode, Simulator, or real hardware.
