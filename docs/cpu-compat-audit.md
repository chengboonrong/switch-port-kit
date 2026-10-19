# A17 Pro CPU source inventory

Run against a separate, local clone of nxnative:

```sh
python3 tools/cpu_compat_audit.py --upstream ~/nxnative --output ~/cpu-inventory.json
```

The scanner searches textual build flags, selected ARM64 atomics and assembly directives. It excludes build directories and never writes file contents. Paths and line numbers are **relative to the upstream repository**.

**Limitations:** Matches can occur in comments; generated code and binary machine instructions are not analyzed. Absence of matches proves nothing. Seeing LSE atomics does not by itself imply they are unsupported by A17 Pro. The `-mcpu=apple-a18` flag requires a separate toolchain and binary disassembly audit. This tool cannot establish A17 Pro compatibility or detect runtime issues.

No proprietary game binaries or files are required.
