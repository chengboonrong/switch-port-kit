# First target: Shin chan — Me and the Professor on Summer Vacation

**Status:** Candidate selected; no nxnative profile created, no confirmed Switch game engine, no successful boot, and no physical iPad test.

Issue: [#4](https://github.com/chengboonrong/switch-port-kit/issues/4).

## Why no fake game profile

nxnative identifies a title from an actual **base title ID**, and maps modules to exact **NSO Build IDs** and known versions. Shader facts, map tables and memory sizing are generated from the legally held game's content, not reliably inferred from promotional websites or the game's PC version. Hard-coding a guessed title ID, Unity version or shader data would create an invalid profile.

## Stage 1 — preflight (no game content read)

Clone nxnative separately and keep your personal files outside any git repository. Run:

```sh
python3 tools/shinchan_preflight.py --game-dir "$HOME/Games/ShinChan" --nxnative "$HOME/nxnative"
```

This only checks that directories and the upstream builder exist and counts top-level `.nsp` entries. It does **not** validate actual game identity, licensing, updates, encryption keys or file integrity.

## Stage 2 — private survey (requires local legally sourced game files)

After dependencies are installed, consult the current nxnative CLI help before proceeding:

```sh
python3 "$HOME/nxnative/scripts/build_ipa_from_nsp.py" --help
```

On builds supporting `--survey-only`, run the following **locally**, substituting paths you control:

```sh
cd "$HOME/nxnative"
python3 scripts/build_ipa_from_nsp.py "$HOME/Games/ShinChan" -k "$HOME/keys/prod.keys" --survey-only
```

**Do not commit or upload** NSPs, keys, extracted files, shader dumps, IPAs or a raw survey until reviewed for embedded copyrighted content and identifying paths. Only share a manually sanitized summary of title ID, build IDs, SDK/engine evidence, graphics API, imports and blocker counts. The command touches real game files locally; the preflight tool does not.

## Stage 3 — profile research checklist

- [ ] Exact base title ID / region and version recorded privately
- [ ] Exact main and SDK NSO Build IDs (not guessed)
- [ ] Engine and graphics API confirmed from Switch binaries
- [ ] Module list and rewritten-site survey compared with nxnative HLE
- [ ] RomFS structure and shader container path recorded **without assets**
- [ ] Memory profile sized from actual binary survey
- [ ] NVN/vulkan route and required shader passes identified
- [ ] Upstream licensing respected for any reused profile files
- [ ] Review sanitized logs for secrets and local paths

**Gate:** do not mark gameplay supported until real iPad launch → menu → gameplay → save/load evidence.
