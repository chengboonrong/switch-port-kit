# 2048 NRO dynamic-symbol audit

This tool reads the NRO MOD0 dynamic table, DT_HASH, DT_SYMTAB and DT_STRTAB without executing or extracting code. The count uses the traditional SysV hash table's nchain field. It also reports init/fini metadata.

On the supplied 2048 sample, DT_HASH at 0x2b0a0 reports 1 bucket and 3 symbols; DT_STRSZ=1. Names appear absent, so dynamic symbol resolution may not be the primary obstacle. This does **not** establish the absence of runtime services, static calls, relocations or embedded import mechanisms. Inspect libnx's startup code and service calls separately.

No game binaries or keys should be committed. This is not an NRO loader and proves no device compatibility.
