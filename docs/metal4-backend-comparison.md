# Metal backend comparison: nxnative vs D2R Mobile

Research: 2026-10-20. Source audit only; no A17 Pro device execution.

## Directly observed

- nxnative `dm/gfx/nvn/nvn_mtl.m` declares both `id<MTLCommandQueue> g_q` and `id<MTL4CommandQueue> g_q4`, alongside MTL4 command allocators, buffers and argument tables.
- nxnative `dm/ios/project.yml` has iOS 26 deployment and `-mcpu=apple-a18`.
- d2r-mobile `dm/ios/project.yml` ALSO sets iOS 26 due to Metal 4, despite its README mentioning an older-API build.
- d2r-mobile `dm/gfx/metal/mtl_backend.m` uses the classic Metal `MTLCommandQueue` API, but this is not evidence that its complete NVN gameplay renderer can run entirely without Metal 4.
- Neither project's published README demonstrates an independently verified full nxnative gameplay test on iPad mini A17 Pro.

## Engineering implications

1. A blanket Metal 3 fallback is **not** a minor compatibility change. nxnative's main rendering architecture depends on MTL4 argument tables, command buffers and allocators.
2. The presence of the older API in an isolated backend does not make that backend a drop-in replacement.
3. An A17 Pro compatibility probe should test concrete Metal 4 object creation and command encoding, using a game-free workload, plus exact OS/GPU feature checks.
4. Audit A18 compiler settings separately with emitted instruction analysis, not broad claims based on text matches.
5. Keep nxnative as the sole primary HLE runtime; use D2R Mobile as architectural prior art only.

## Sources

- https://github.com/seedds/nxnative/blob/main/dm/gfx/nvn/nvn_mtl.m
- https://github.com/seedds/nxnative/blob/main/dm/ios/project.yml
- https://github.com/d2r-mobile/d2r-mobile/blob/main/dm/ios/project.yml
- https://github.com/d2r-mobile/d2r-mobile/blob/main/dm/gfx/metal/mtl_backend.m

**Do not interpret this document as device support or game compatibility evidence.**
