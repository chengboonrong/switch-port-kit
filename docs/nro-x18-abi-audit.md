# Partial ARM64 x18 candidate inventory

Run `from tools.nro_x18_audit import audit_x18` on an authorized, locally held NRO image. The tool examines **only** ADD/SUB immediate, LDR/STR unsigned offset and MOV-wide immediate encodings. Other encodings (including register-register arithmetic, branches and many addressing modes) are **not** handled. It does not do control flow, relocation, execution, instruction rewriting or automatic x18 ABI adaptation.

Uploaded 2048.nro, local read-only scan:
- ADD/SUB immediate involving x18: 6 candidate words
- LDR/STR unsigned offset involving x18: 4 candidate words
- MOV wide involving x18: 3 candidate words
- **13 candidates total in this partial subset**. Do not call this the total x18 use count.
- Some candidates may be inline data in the text region.

On Apple ARM64, x18 is platform-reserved. Future native port options must preserve Apple's ABI and use signed, ahead-of-time linked code; naive binary branch/load/execute is not a supported iPadOS distribution model. No game binary or keys are included in this repository.
