# Metal 4 dependency inventory (source audit)

Date: 2026-10-20. Target: iPad mini A17 Pro. This is a **source review**, not hardware confirmation.

## Confirmed from nxnative repository

- `dm/ios/project.yml` targets iOS 26 and explicitly cites `MTL4CommandQueue` as one reason for the deployment minimum.
- `dm/gfx/nvn/nvn_rtex.inc` uses `MTL4ArgumentTable` and describes rendering work encoded on a Metal 4 command buffer for extrapolation.
- `dm/gfx/tex/nvn_deswizzle_gpu.h` declares `nvn_deswz_gpu_encode_m4` taking `MTL4ComputeCommandEncoder` and `MTL4ArgumentTable`.
- `dm/gfx/tex/nvn_deswizzle_gpu.m` implements that Metal 4 deswizzle path.
- `dm/gfx/tests/t_rt_range.m` constructs `MTL4RenderPassDescriptor` test cases.
- `dm/ios/project.yml` includes `-mcpu=apple-a18`, potentially relevant when producing an executable for A17 Pro.

## What these findings do NOT prove

Mention of Metal 4 types is not by itself proof that *every* Metal 4 feature is required at run time or that the target A17 Pro does or does not support it. Likewise, `-mcpu=apple-a18` does not prove incompatible machine instructions were emitted. The project must not claim support or lack of support without specific feature and disassembly evidence.

## Verification plan

1. Pin one upstream commit SHA and inventory all `MTL4*` usages, not only code search excerpts.
2. Group uses into mandatory render-loop requirements vs optional optimizations.
3. Identify any feature-family checks and availability guards at each call site.
4. Produce CPU disassembly of a game-free host test build for auditing compiler-generated instructions.
5. Compare reported capabilities with actual iPad mini A17 Pro hardware tests.
6. Only propose a conditional fallback after understanding complete command submission and resource binding semantics.

## Sources

- https://github.com/seedds/nxnative/blob/main/dm/ios/project.yml
- https://github.com/seedds/nxnative/blob/main/dm/gfx/nvn/nvn_rtex.inc
- https://github.com/seedds/nxnative/blob/main/dm/gfx/tex/nvn_deswizzle_gpu.h
- https://github.com/seedds/nxnative/blob/main/dm/gfx/tex/nvn_deswizzle_gpu.m
- https://github.com/seedds/nxnative/blob/main/dm/gfx/tests/t_rt_range.m
