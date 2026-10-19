# Roadmap

## PR 1 — Repository and upstream audit
- [x] Initialize public repository
- [ ] Audit nxnative license, build pipeline, iPad device gates, GPU dependencies and iOS signing
- [ ] Record findings with pinned upstream revisions
- [ ] Determine initial legally sourced, version-matched test title

## PR 2 — iPad mini A17 Pro Metal probe
- [x] Add XcodeGen project and standalone SwiftUI app
- [x] Report Metal device, GPU family, BC support and texture-allocation results
- [ ] Compile with Xcode on macOS (not yet verified)
- [ ] Deploy and run on physical iPad mini A17 Pro (not yet verified)
- [ ] Test BC1/BC3/BC7 actual sampling, render output and pixel readback
- [ ] Add optional JSON export and anonymized test report schema

## PR 3 — Compatibility patch
- [ ] Propose changes only after device results
- [ ] Prefer capability checks over fixed device whitelist

## PR 4 — Supported-title test
- [ ] Privately build game-specific app using legally obtained inputs
- [ ] Capture build/runtime diagnostics without keys or game assets

## PR 5 — Reliability and performance
- [ ] Validate menu, gameplay, controls, audio and save/load
- [ ] Benchmark memory, thermals and frame times

## How to run the probe

Requires macOS with current Xcode, [XcodeGen](https://github.com/yonaskolb/XcodeGen), an Apple development team for physical-device signing, and an iPad mini A17 Pro.

```sh
brew install xcodegen
xcodegen generate
open A17ProMetalProbe.xcodeproj
```

Select the app target, set your own unique bundle identifier and signing Team under Signing & Capabilities, select the attached iPad mini, then build and run. Tap **Run Probe** and share the report after reviewing it for identifying information.

**Important:** The initial probe only tests device-reported capabilities and allocation of BC texture resources. It does not yet validate BC pixel uploads, shader sampling, correct colors, game compatibility, or performance. The deployment minimum in the probe is iOS 18 and does not assert nxnative support on iOS 18.
