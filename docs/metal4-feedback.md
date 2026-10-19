# Metal 4 completion feedback smoke test

The native physical-device test now attaches an `MTL4CommitOptions` feedback handler and waits for it with a bounded 3-second timeout. It returns `FEEDBACK_RECEIVED_EMPTY` when the callback runs, or `TIMEOUT_EMPTY` otherwise.

This uses Apple's documented Metal 4 commit-feedback callback; it does **not** verify a compute shader, memory writeback, output pixel correctness or game compatibility. The command buffer is empty, and the simulator intentionally skips this path.

The timeout protects the app from an indefinite hang, not from all GPU driver crashes. A test result from a real iPad mini A17 Pro remains necessary. Future tests should encode actual Metal 4 compute/blit work and verify written bytes before reporting GPU execution as validated.

References: https://developer.apple.com/documentation/metal/mtl4commitoptions and https://developer.apple.com/documentation/metal/mtl4commitfeedbackhandler
