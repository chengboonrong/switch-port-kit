#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <TargetConditionals.h>

// A game-free Metal 4 submission probe. An empty command buffer proves queue,
// allocator and command-buffer creation and submission, NOT shader execution.
NSString *SPKMetal4SubmitProbe(id<MTLDevice> device) {
#if TARGET_OS_SIMULATOR
    return @"metal4_native_submit: SKIPPED_SIMULATOR";
#else
    if (@available(iOS 26.0, *)) {
        NSError *error = nil;
        MTL4CommandQueueDescriptor *queueDescriptor = [MTL4CommandQueueDescriptor new];
        queueDescriptor.feedbackQueue = dispatch_get_global_queue(QOS_CLASS_UTILITY, 0);
        id<MTL4CommandQueue> queue = [device newMTL4CommandQueueWithDescriptor:queueDescriptor error:&error];
        if (!queue) return [NSString stringWithFormat:@"metal4_native_submit: FAIL_QUEUE %@", error.localizedDescription ?: @""];
        MTL4CommandAllocatorDescriptor *allocatorDescriptor = [MTL4CommandAllocatorDescriptor new];
        id<MTL4CommandAllocator> allocator = [device newCommandAllocatorWithDescriptor:allocatorDescriptor error:&error];
        if (!allocator) return [NSString stringWithFormat:@"metal4_native_submit: FAIL_ALLOCATOR %@", error.localizedDescription ?: @""];
        id<MTL4CommandBuffer> buffer = [device newCommandBuffer];
        if (!buffer) return @"metal4_native_submit: FAIL_BUFFER";
        [buffer beginCommandBufferWithAllocator:allocator];
        [buffer endCommandBuffer];
        id<MTL4CommandBuffer> buffers[] = { buffer };
        dispatch_semaphore_t done = dispatch_semaphore_create(0);
        MTL4CommitOptions *options = [MTL4CommitOptions new];
        [options addFeedbackHandler:^(id<MTL4CommitFeedback> feedback) {
            (void)feedback;
            dispatch_semaphore_signal(done);
        }];
        [queue commit:buffers count:1 options:options];
        long waitResult = dispatch_semaphore_wait(
            done, dispatch_time(DISPATCH_TIME_NOW, 3 * NSEC_PER_SEC));
        // The feedback callback signals completion of the empty submission.
        // It does not validate actual GPU rendering or memory correctness.
        return waitResult == 0
            ? @"metal4_native_submit: FEEDBACK_RECEIVED_EMPTY"
            : @"metal4_native_submit: TIMEOUT_EMPTY";
    }
    return @"metal4_native_submit: UNSUPPORTED_OS";
#endif
}
