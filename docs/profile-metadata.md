# Profile metadata gate

Before attempting a version-specific nxnative profile, create a **private**, manually verified JSON summary containing only:

```json
{
  "title_id": "010015100B514000",
  "graphics": "nvn",
  "module_build_ids": {"main": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
  "evidence": "locally_verified"
}
```

**Important:** The values above are synthetic examples from an unrelated game and **do not identify Shin chan**. Do not copy them into a real profile.

Run `python3 tools/profile_metadata.py /private/path/metadata.json` locally. A successful validation only establishes shape and presence; it does not prove that information is correct, that the game is supported, or that the title will run. Never commit your raw survey, NSP files, keys or shader assets.

This deliberately does not generate `game.tsv`: nxnative game profiles require additional measured game-specific memory, shader and import data. Validation is a preparation step, not a working port.
