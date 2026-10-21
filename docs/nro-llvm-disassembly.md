# Offline AArch64 disassembly of an NRO

The CLI `tools/nro_llvm_disasm.py` wraps an NRO text segment in an **analysis-only** ELF64 AArch64 object and runs a local `llvm-objdump`. It never executes guest instructions and does **not** create a valid port, native binary or IPA.

```sh
python3 tools/nro_llvm_disasm.py /private/2048.nro --output /private/2048-disassembly.txt
```

Verified locally with LLVM 17's AArch64 disassembler on a user-supplied 2048 NRO. The NRO's first instruction decodes as a branch to `0x80`. The wrapped ELF preserves the original NRO-relative code offsets (the first bytes are header/trampoline data and may decode as nonsensical instructions). Disassembly has **no control-flow reachability guarantee**.

**Privacy:** the transient wrapper and disassembly contain guest code. Use only files you have rights to analyze; do not commit generated ELF/disassembly to public Git. The temporary ELF is deleted after disassembly. For large output, use `--output` and keep the file outside public checkouts.
