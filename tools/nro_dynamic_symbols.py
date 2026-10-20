"""Read-only NRO dynamic symbol / init-fini inventory; never executes code."""
import struct

def inspect_dynamic_symbols(blob: bytes) -> dict:
    if len(blob) < 0x80 or blob[0x10:0x14] != b"NRO0":
        raise ValueError("invalid NRO")
    image_size = struct.unpack_from("<I", blob, 0x18)[0]
    if not 0x80 <= image_size <= len(blob):
        raise ValueError("invalid image size")
    mod = struct.unpack_from("<I", blob, 4)[0]
    if mod > image_size - 0x1c or blob[mod:mod+4] != b"MOD0":
        raise ValueError("invalid MOD0 pointer")
    dyn = mod + struct.unpack_from("<i", blob, mod+4)[0]
    if dyn < 0 or dyn > image_size - 16:
        raise ValueError("invalid dynamic table")
    tags = {}
    for index in range(512):
        pos = dyn + 16*index
        if pos+16 > image_size:
            raise ValueError("unterminated dynamic table")
        tag, value = struct.unpack_from("<QQ", blob, pos)
        if tag == 0:
            break
        if tag in tags and tags[tag] != value:
            raise ValueError("conflicting dynamic tag")
        tags[tag] = value
    else:
        raise ValueError("dynamic table too long")
    if not all(t in tags for t in (4,5,6,10,11)):
        raise ValueError("missing required symbol metadata")
    h, strings, symbols, strsize, entry_size = (tags[t] for t in (4,5,6,10,11))
    if entry_size != 24 or h > image_size-8 or strsize > image_size or strings > image_size-strsize:
        raise ValueError("invalid symbol table metadata")
    buckets, count = struct.unpack_from("<II", blob, h)
    if not buckets or not count or count > 100_000 or symbols > image_size or count > (image_size-symbols)//24:
        raise ValueError("invalid SysV hash symbol count")
    if buckets > (image_size-h-8)//4 or count > (image_size-h-8-4*buckets)//4:
        raise ValueError("hash table outside image")
    named = 0
    undefined = 0
    exported = 0
    for i in range(count):
        name_off, info, other, section, value, size = struct.unpack_from("<IBBHQQ", blob, symbols+i*24)
        if name_off >= strsize:
            raise ValueError("symbol name outside string table")
        if name_off:
            end = blob.find(bytes([0]), strings+name_off, strings+strsize)
            if end < 0:
                raise ValueError("unterminated symbol name")
            named += 1
        if section == 0 and i:
            undefined += 1
        if section != 0 and (info >> 4) in (1,2):
            exported += 1
    return {"schema_version":1,"symbol_count":count,"named_symbol_count":named,
            "undefined_symbol_count":undefined,"global_defined_count":exported,
            "string_table_bytes":strsize,
            "init_function_offset":tags.get(12),"fini_function_offset":tags.get(13),
            "init_array_offset":tags.get(25),"init_array_bytes":tags.get(27,0),
            "fini_array_offset":tags.get(26),"fini_array_bytes":tags.get(28,0),
            "execution_performed":False,"iPad_compatibility_proven":False}
