#!/usr/bin/env python3
"""Wrap a local NRO text segment in an analysis-only AArch64 ELF for llvm-objdump.

Generated ELF contains original guest bytes. Keep it private; never execute it.
"""
import argparse
from pathlib import Path
import struct
import subprocess
import tempfile

MAX_NRO = 256 * 1024 * 1024


def make_analysis_elf(nro: bytes) -> bytes:
    if len(nro) < 0x80 or nro[0x10:0x14] != b"NRO0":
        raise ValueError("invalid NRO0 header")
    image_size = struct.unpack_from("<I", nro, 0x18)[0]
    off, size = struct.unpack_from("<II", nro, 0x20)
    if not (0x80 <= image_size <= len(nro) and off % 4 == size % 4 == 0
            and off <= image_size and size <= image_size - off and size):
        raise ValueError("invalid text segment")
    text = nro[off:off + size]
    names = b"\x00.text\x00.shstrtab\x00"
    start = 0x1000
    string_start = start + len(text)
    shoff = (string_start + len(names) + 7) & ~7
    out = bytearray(shoff + 64 * 3)
    out[0:7] = bytes((127, 69, 76, 70, 2, 1, 1))
    # ELF64 ET_EXEC, EM_AARCH64, one read+execute PT_LOAD.
    struct.pack_into("<HHIQQQIHHHHHH", out, 16,
                     2, 183, 1, 0, 64, shoff, 0, 64, 56, 1, 64, 3, 2)
    struct.pack_into("<IIQQQQQQ", out, 64, 1, 5, start, off, 0,
                     len(text), len(text), 0x1000)
    out[start:start+len(text)] = text
    out[string_start:string_start+len(names)] = names
    struct.pack_into("<IIQQQQIIQQ", out, shoff+64, 1, 1, 6,
                     off, start, len(text), 0, 0, 4, 0)
    struct.pack_into("<IIQQQQIIQQ", out, shoff+128, 7, 3, 0,
                     0, string_start, len(names), 0, 0, 1, 0)
    return bytes(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("nro", type=Path)
    parser.add_argument("--llvm-objdump", default="llvm-objdump")
    parser.add_argument("--output", type=Path, help="private disassembly text destination")
    args = parser.parse_args()
    if args.nro.is_symlink() or not args.nro.is_file() or args.nro.stat().st_size > MAX_NRO:
        parser.error("expected a regular local NRO, at most 256 MiB")
    elf = make_analysis_elf(args.nro.read_bytes())
    with tempfile.TemporaryDirectory(prefix="nro-disasm-") as d:
        path = Path(d) / "analysis.elf"
        path.write_bytes(elf)
        result = subprocess.run([args.llvm_objdump, "--no-show-raw-insn", "-d", str(path)],
                                capture_output=True, text=True, check=False)
    if result.returncode:
        parser.error("llvm-objdump failed; verify it supports AArch64")
    if args.output:
        if args.output.is_symlink():
            parser.error("refusing symlink output")
        args.output.write_text(result.stdout, encoding="utf-8")
        print("Saved PRIVATE disassembly (contains guest instructions):", args.output)
    else:
        print(result.stdout, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
