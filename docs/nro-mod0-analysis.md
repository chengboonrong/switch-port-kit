# NRO MOD0 & dynamic relocation inventory

Run `python3 tools/nro_mod0_inspector.py /private/path/2048.nro` to list MOD0 dynamic entries without executing code. The tool deliberately does **not** apply relocations, decode imported symbols, copy game bytes, or claim iPad compatibility.

Known test sample: 2048 NRO declares a MOD0 structure and compressed relative relocations (DT_RELR / DT_RELRSZ / DT_RELRENT). Before loading code into an iPad app, an authorized native port must correctly map memory segments, implement the relative relocation rules, examine imports and runtime services, and satisfy iOS code-signing restrictions.

The program reports hexadecimal offsets and tag values; these are not a substitute for auditing an actual AArch64 relocator. Any executable port must avoid runtime executable-memory approaches prohibited by iPadOS. Do not upload game binaries or private keys to this public repository.
