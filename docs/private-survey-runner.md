# Private survey runner

This is a convenience wrapper, **not** a sandbox or security boundary. It launches an independently cloned upstream nxnative script and therefore inherits all upstream behavior, permissions and network capabilities. Inspect the pinned upstream commit and verify its `--survey-only` help before executing.

By default it only checks the existence of local paths. It does not inspect game content or verify game identity.

```bash
python3 tools/private_survey_runner.py \
  --nxnative "$HOME/nxnative" \
  --game-dir "$HOME/Games/ShinChan" \
  --keys "$HOME/keys/prod.keys"
```

When you are ready to perform an authorized, private survey, add `--run --log-dir "$HOME/PrivateSwitchSurveyLogs"`. Store both files and logs **outside** your public git checkout; output may contain paths or game-derived content. The runner does not upload anything by itself, but cannot prevent upstream code from networking. Review results manually; do not share raw surveys, keys, dumps, shaders or IPAs. Only a separately reviewed technical summary should enter GitHub.

The runner never claims the game is playable and does not build a game profile.
