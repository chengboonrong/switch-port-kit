# SwiftUI Probe E2E contract

The Probe UI declares stable accessibility identifiers to support future TesterArmy e2e tests:

| Identifier | Expected UI | Action |
|---|---|---|
| `probe.heading` | Research heading | visible |
| `probe.run` | Run Probe button | tap |
| `probe.report` | Diagnostics text | changes after tap |
| `probe.share` | Share Diagnostics | visible |

The first tests should use deterministic locators and assertions; avoid a model dependency unless interaction cannot be located reliably. Follow [e2e integration evaluation](https://github.com/chengboonrong/switch-port-kit/blob/docs/tester-army-e2e-evaluation/docs/tester-army-e2e-evaluation.md).

**Test environment:** iOS Simulator on a macOS runner after a successful Xcode build. No CI workflow or SDK dependency is added yet, because the framework's exact mobile runner API and installed simulator availability must first be verified. Simulator passing cannot prove BC support or A17 Pro hardware compatibility.
