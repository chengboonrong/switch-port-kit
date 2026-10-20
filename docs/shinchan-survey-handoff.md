# Shin chan first port — private survey handoff

**Target:** Shin chan: Me and the Professor on Summer Vacation — The Endless Seven-Day Journey (Nintendo Switch). **No playable port is claimed.**

This document is the concrete boundary between public, game-free SwitchPortKit development and private analysis of an authorized copy of the game. Do not place game dumps, keys, extracted ROM files, shaders, or built IPAs into this public repository.

## Phase 0: current baseline

- Metal Probe and simulator E2E are engineering tests, not Switch game execution.
- The nxnative supported-games list does **not** include Shin chan.
- No validated Switch title ID, NSO Build ID, memory allocation or shader manifest is currently available in SwitchPortKit.
- A guessed game profile would be misleading.

## Phase 1: on a local Mac only

Clone upstream nxnative into a *separate* directory, outside the public project checkout:

```sh
git clone https://github.com/seedds/nxnative.git "$HOME/nxnative"
cd "$HOME/nxnative"
git rev-parse HEAD
python3 scripts/build_ipa_from_nsp.py --help
```

Place your legitimately obtained base and update NSP files in a private directory (for example, `$HOME/Games/ShinChan`), and keep your own keys under a different private path. **Do not push those files.** Check the upstream tool's documented flags against the current revision before running it.

Run the project preflight:

```sh
cd "$HOME/switch-port-kit"
python3 tools/shinchan_preflight.py \
  --game-dir "$HOME/Games/ShinChan" \
  --nxnative "$HOME/nxnative"
```

The preflight counts NSP-like filenames; it does **not** validate that they are Shin chan or that they are safe/correct game files.

Then perform a **private, offline, survey-only** pass from nxnative, provided your checked-out build exposes `--survey-only`:

```sh
cd "$HOME/nxnative"
python3 scripts/build_ipa_from_nsp.py \
  "$HOME/Games/ShinChan" \
  -k "$HOME/keys/prod.keys" \
  --survey-only
```

This is a *local* command that reads game files. The exact extraction/survey behavior depends on the pinned upstream revision; it does not imply an IPA was built or will boot.

## Phase 2: manually extract **only non-asset technical facts**

Record, privately first:

| Field | Why needed | Evidence |
|---|---|---|
| nxnative git commit SHA | reproducibility | local `git rev-parse HEAD` |
| base title ID and game version | profile identity | extracted control metadata |
| main and SDK NSO Build IDs | safe, version-pinned patching | binary survey |
| module list / service imports | HLE planning | binary survey |
| game engine and Switch graphics API | shader route | binary survey |
| shader container categories/counts | translator strategy | survey, *not shader binaries* |
| guest memory and heap notes | iPad compatibility | measured host behavior, if available |

**Do not publish the original survey.** It may contain local paths or copyrighted derived information. The existing `survey_sanitizer.py` is conservative and may not understand real nxnative report headings: review the JSON and treat missing fields as unknown, not zero.

## Phase 3: triage gates

1. **Identity known?** If title ID or Build IDs are missing, stop; do not create `dm/games/<id>/game.tsv`.
2. **Graphics route known?** Classify as NVN, Vulkan, or unknown; unknown is a blocker.
3. **System imports matched?** List missing Horizon calls as *counts and symbol identifiers*, not extracted code.
4. **Shader extraction understood?** Only then plan generated shader tables.
5. **No hardware evidence yet?** Keep iPad mini A17 Pro compatibility status **untested**, regardless of simulator CI.
6. **Legal review:** Keep the public source-only repository separate from personally built software containing copyrighted game material.

## Next concrete engineering deliverable

Using a sanitized, reviewed metadata summary and pinned nxnative commit, create `docs/shinchan-compatibility-matrix.md` with per-module HLE and per-renderer blockers, then implement an initial **version-specific** nxnative profile in a private/local worktree. If the profile is suitable for public contribution, remove game assets, keys and personal paths and preserve upstream licenses before sharing it.

Tracked in [Issue #4](https://github.com/chengboonrong/switch-port-kit/issues/4).
