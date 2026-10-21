# Additional x18 instruction family: shifted-register ADD/SUB

The x18 audit now scans ADD/SUB (shifted register) operands **Rd, Rn and Rm**. This also recognizes the encoding used by SUBS, including the CMP alias (Rd = XZR/WZR). It remains a partial static candidate scan; other instruction families and control-flow reachability are not analyzed.

Read-only verification against the user-provided `2048.nro`:
- Text segment size: **176128 bytes**
- Additional shifted-register SUBS/CMP encoding candidates using x18: **2**
- Both encode the word `0x6b00025f`, at NRO-relative byte offsets `0x5f68` and `0x6064`.
- Prior three-family scan reported 13 x18 candidates; this fourth-family extension brings the **covered-family** candidate count to 15 for this sample, not a complete x18 count.
- No guest ARM64 instructions have been executed or patched.

The NRO remains local and is not committed to the repository.
