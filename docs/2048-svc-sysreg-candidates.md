# 2048 NRO SVC and system register candidates

This scanner records **static instruction encoding candidates**, not executed service calls. AArch64 SVC immediates identify stubs; exact Horizon service functionality requires independent ABI mapping.

Real uploaded 2048 NRO local analysis (no binary committed):
- SVC candidate immediates (one occurrence each): `0x1,0x2,0x3,0x5,0x6,0x7,0xb,0x13,0x14,0x15,0x16,0x17,0x18,0x1a,0x1b,0x1c,0x1d,0x1f,0x21,0x26,0x28,0x29,0x52`
- MRS `S3_3_C13_C0_3`: 174 candidates (architectural TPIDRRO_EL0)
- MRS `S3_3_C14_C0_1`: 12 candidates (CNTVCT_EL0)
- Other system register candidates need independent interpretation.

Nothing above proves which instructions are reachable, which services are supported on iPad, or a viable loader. Do not conflate disassembly counts with execution trace.
