# TesterArmy e2e integration assessment

External framework: https://github.com/tester-army/e2e (Apache-2.0).

## Decision

**Adopt later as an optional simulator UI smoke-testing layer, not as a hardware compatibility oracle.**

The framework's README documents web and mobile agents, iOS simulators, a SwiftUI example, and model-backed natural-language actions; it uses `npx e2e init`. Its APIs may change before 1.0. Usage telemetry can be disabled with `E2E_TELEMETRY_DISABLED=1`.

## Test tiers

| Tier | Runner | Checks | Claims we cannot make |
|---|---|---|---|
| 0 | Ubuntu Python CI | Metadata and survey validators | iPad compatibility |
| 1 | macOS/Xcode build | Swift syntax, app packaging | Physical GPU correctness |
| 2 | iOS simulator + e2e | App launch, Run Probe button, diagnostics copy/share UI | A17 Pro BC texture support, gaming |
| 3 | Physical iPad mini A17 Pro | Actual BC sampling, Metal performance, nxnative execution | Other games/OS versions |

## Implementation prerequisites

- First merge/test the existing SwiftUI probe PR #1.
- Validate exact CLI and package version using the framework's packaged documentation before pinning dependencies.
- Use a macOS CI runner for simulator testing and explicitly budget its cost.
- Begin with deterministic native UI assertions; introduce model-backed agent actions only where necessary.
- Use no game binaries, keys, commercial screenshots, or real user diagnostics in hosted tests.
- Disable CLI telemetry in CI, and keep model tokens/credentials in GitHub Actions Secrets if needed.
- Avoid installing unreviewed dependencies directly into the main workflow.

## Planned E2E cases

1. Probe app launches and presents “Run Probe”.
2. Tapping “Run Probe” displays a diagnostic report or an understandable no-Metal error.
3. “Share Diagnostics” exists and exposes the generated report.
4. App can be backgrounded and foregrounded without losing the current report.

## Acceptance

An optional, separately triggered CI workflow passing on a pinned framework version and simulator; results must explicitly state “simulator UI tests only”. Do not use this to bypass or replace physical A17 Pro validation.

## Sources

- https://github.com/tester-army/e2e
- https://e2e.tester.army/docs/quickstart
