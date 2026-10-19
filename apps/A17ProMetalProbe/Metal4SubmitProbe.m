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
        [queue commit:buffers count:1 options:nil];
        return @"metal4_native_submit: SUBMITTED_UNVERIFIED";
    }
    return @"metal4_native_submit: UNSUPPORTED_OS";
#endif
}
