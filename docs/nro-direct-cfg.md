# 2048 NRO direct-branch candidate graph

The `tools/nro_direct_cfg.py` function starts at the NRO text entry offset and explores direct AArch64 B, BL, B.cond, CBZ/CBNZ and TBZ/TBNZ edges, plus fallthrough. It stops at BR/RET and records BLR as an unresolved indirect frontier while continuing its fallthrough.

**This is an approximate static graph, not proof of executable reachability.** It does not resolve BR/BLR, exception returns, function pointers or jump tables; inline data may be mistaken for instructions. It does not run ARM64 instructions.

Read-only local measurements on the user-supplied `2048.nro`:
- 44,032 four-byte instruction slots in the declared text region
- 25,198 distinct candidate graph locations traversed
- 631 unresolved indirect/return boundaries
- 22 SVC candidate encodings in the graph, compared with 23 from linear scanning
- Zero out-of-text direct edges observed

The missing SVC candidate is **not** proven unreachable. The result is not a usable iPad loader or Horizon compatibility layer. No original NRO bytes are included in this repository.

Usage from the repository root:

```python
from pathlib import Path
from tools.nro_direct_cfg import analyze_entry
report = analyze_entry(Path("/private/2048.nro").read_bytes())
print(report)
```
