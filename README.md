# SwitchPortKit

Experimental open-source research toolkit for **native porting of compatible Nintendo Switch games to Apple devices**. First hardware target: **iPad mini (A17 Pro)**.

> **Status: research / pre-alpha.** No Nintendo Switch game is currently claimed to run through this project. This is not an emulator, a one-click game converter, or an existing working compatibility layer.

## Project goals

1. Audit [nxnative](https://github.com/seedds/nxnative) for iPad mini A17 Pro compatibility.
2. Build a standalone native Metal capability probe to validate Apple GPU features on the physical device.
3. Propose evidence-backed compatibility changes upstream where practical.
4. Document reproducible build steps and real device-test results.

## Scope and safety

- No commercial game ROMs, NSP/XCI files, copyrighted assets, firmware, encryption keys, or game-specific decryption material in this repository.
- Respect upstream project licenses. No nxnative source has been copied into this repository.
- Apple code signing and platform constraints are not to be bypassed.
- Compatibility is game- and version-specific. We will never describe untested hardware or games as supported.

## Roadmap

See [`docs/roadmap.md`](docs/roadmap.md) once the first development PR is merged.

## Acknowledgements

Inspired by [nxnative](https://github.com/seedds/nxnative) and [ns-game-apple-arm-port](https://github.com/realskyrin/ns-game-apple-arm-port). These are independent projects; no affiliation is implied.

## License

**Undecided.** A license will be selected after reviewing dependencies and contribution requirements. Until then, no permission for third-party redistribution or modification is granted beyond applicable law.
