# Shin chan: survey evidence to actual nxnative work

**Status:** Research only. The exact Nintendo Switch executable version and Title ID of Shin chan have **not** been verified. No game profile or playable build exists.

This document maps the **actual upstream survey** to engineering changes, using [nxnative/docs/agents/02-survey.md](https://github.com/seedds/nxnative/blob/main/docs/agents/02-survey.md). The survey itself must remain private.

## Stage 1 — fixed-version survey (on the developer's Mac, not CI)

1. Pin an upstream nxnative commit: `git -C ~/nxnative rev-parse HEAD`.
2. Verify help for `--survey-only`, and run only against a legally acquired local base game and updates.
3. Compare the survey's **control metadata name** against the intended *Shin chan: Me and the Professor on Summer Vacation*; a filename is not sufficient for identity.
4. Do not commit the generated `survey.md`: the upstream manifest may expose **RomFS filenames, sizes and the first 32 bytes of files**. Treat it as potentially game-derived copyrighted data.
5. Prepare a manually reviewed, sanitized evidence summary. Existing sanitizer only recognizes narrow line formats and may not parse the real report; **never assume blank fields mean zero**.

## Stage 2 — evidence matrix and actual code targets

| Survey evidence | Verify | Specific nxnative files or next command | Blocker if absent |
|---|---|---|---|
| NACP title + version, program ID | correct game and region | `dm/games/game.py`, new game's `game.tsv` | Cannot name profile |
| ExeFS modules + each NSO Build ID | exact version lock | `dm/tools/patch_nso.py`, `dm/games/<id>/game.tsv` | Cannot safely patch game code |
| SDK and engine markers | Switch binary's SDK/Unity/IL2CPP evidence | `docs/agents/02-survey.md` | Cannot select engine-specific handling |
| NVN / Vulkan / EGL markers | actual rendering route | `dm/gfx/nvn` or `dm/gfx/vk` | Cannot plan shaders |
| Instruction census | SVC, x18, TPIDR, cache ops, exclusive atomics | `dm/tools/insn_census.py` → `patch_nso.py` | Incomplete native ARM64 rewrite |
| Dynamic imports vs host hooks | which external services are needed | `dm/tools/nso_syms.py`, `dm/host` | Unknown Horizon HLE gaps |
| RomFS container types | shaders embedded in which container type | `dm/gfx/tools/shader_split.py` | No translated Metal shaders |
| Memory/heap requirements | profile address-space partition | `dm/games/profile_guess.py`, host heap checks | Memory mapping failures |

**Important:** An unhooked dynamic import does not necessarily imply a missing HLE service; many SDK functions execute normally in guest code. Only treat as required hooks after examining how the service reaches the host or after an actual bring-up failure.

## Stage 3 — private profile bring-up order

A. Confirm identity → B. prove rewriter census and patched site counts agree → C. fill module list, exact Build IDs and memory facts → D. determine graphics/shader containers → E. generate shader tables → F. attempt Mac host boot with local assets → G. classify first actual failure via `docs/agents/03-bringup.md` → H. only then try an iPad build.

No arbitrary guessed `game.tsv`, no fake Shader Manifest, no force-enable of device whitelist and no false playable claim.

## Immediately actionable without game assets

- Keep SwiftUI A17 Pro Metal probe CI green.
- Pin nxnative and verify the survey CLI surface before making a local survey.
- Keep the public issue's blockers separate: **device/runtime** vs **per-game profile**.
- Prepare the sanitized evidence matrix for manual completion after the local survey.

## Privacy and reproducibility

Public issue updates may include manually reviewed technical metadata; never paste raw ExeFS, RomFS, key files, game code, shader contents or original survey output. Confirm whether any metadata is appropriate for public distribution. Use exact revision references to make future assessments repeatable.

Tracked in [Issue #4](https://github.com/chengboonrong/switch-port-kit/issues/4).
