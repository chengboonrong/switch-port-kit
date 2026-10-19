# Sharing nxnative game survey results safely

This repository deliberately never uploads game files or raw nxnative survey data.

## Usage

From the SwitchPortKit project root:

```sh
python3 tools/survey_sanitizer.py "/private/path/survey.md" --output "/private/path/safe-summary.json"
```

The tool emits **only** strictly formatted lines for `Title ID`, `Graphics`/`Graphics API`, and `Module count`. Actual nxnative survey formatting may differ; missing output fields are expected and do not imply that the original survey lacked the underlying data. Never fabricate omitted fields.

The tool never prints paths, shader dumps, filenames, raw text, game binaries or keys. Still review each value and the generated JSON before sharing. Do not store raw reports inside this repository. **This is an allowlist metadata extractor, not a guarantee that publishing metadata is legally permissible.**

Run local tests: `python3 -m unittest discover -s tests -v`.

## Next task

Once actual safe sample reports are obtained, document their structure, update the extractor's anchored field patterns, and add synthetic test fixtures only (no copyrighted data).
