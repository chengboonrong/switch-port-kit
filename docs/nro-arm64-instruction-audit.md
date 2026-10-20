# 2048 NRO: selected AArch64 instruction inventory

The read-only scanner searches 4-byte words in the declared NRO text section for AArch64 SVC/HVC/SMC instructions and MRS/MSR (register) instruction families.

Sample (user-supplied `2048.nro`, analyzed locally, not checked into Git):
- Text: 176,128 bytes
- SVC candidate words: **23** (first offset `0x6fb8`)
- HVC / SMC: **0 / 0**
- MRS-family candidates: **196**
- MSR-register-family candidates: **1**

**Important:** instruction-family scanning is not a control-flow-aware disassembly. Inline literal data or unreachable instructions may be counted; the scanner does not establish that a particular SVC executes. The MRS count does not show which system registers are accessed. In addition, x18 usage is **not yet inspected**. This is strictly a candidate inventory, not evidence the binary can run on iPadOS.

Usage (repo root): `python3 -c 'import json,sys; from tools.nro_arm64_audit import audit_arm64_text; print(json.dumps(audit_arm64_text(open(sys.argv[1],"rb").read()),indent=2))' /private/2048.nro`

Next: decode actual SVC immediates and referenced system-register fields using a maintained AArch64 decoder, inspect reachable call sites, then design code-signing-compatible native port boundaries.
