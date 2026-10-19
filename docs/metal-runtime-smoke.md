# Metal runtime smoke probe

The physical-device diagnostics now include:

- iOS 26 availability gate for Metal 4 API exposure
- Objective-C runtime visibility of four Metal 4 protocol names
- Real classic Metal command buffer submission using a blit fill and CPU-side byte verification

**Limitations:** Protocol visibility does not establish feature support. The smoke submission uses **classic Metal**, not MTL4 commands. The report explicitly emits `metal4_command_submit: NOT_TESTED`. Simulator uses the existing intentionally restricted diagnostics path and does not represent A17 Pro hardware.

## Follow-up

1. Run and export results from a physical iPad mini A17 Pro.
2. Add an isolated, compile-verified MTL4 command allocator / queue / submission path based on Xcode SDK declarations; no dynamic unsafe invocation.
3. Check feature availability and capture validation diagnostics.
4. Compare behavior against nxnative's concrete Metal 4 requirements, then attempt the game-free runtime build.

No copyrighted game content, keys or shader files are needed.
