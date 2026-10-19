#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <TargetConditionals.h>

// This test is intentionally isolated from commercial game resources.
NSString *SPKMetal4ComputeProbe(id<MTLDevice> device) {
#if TARGET_OS_SIMULATOR
    return @"metal4_compute: SKIPPED_SIMULATOR";
#else
    if (@available(iOS 26.0, *)) {
        NSError *error = nil;
        NSString *source = @"#include <metal_stdlib>\nusing namespace metal;\nkernel void spk_write(device uint* out [[buffer(0)]], uint tid [[thread_position_in_grid]]) { if (tid == 0) out[0] = 0x1234ABCDu; }";
        id<MTLLibrary> library = [device newLibraryWithSource:source options:nil error:&error];
        id<MTLFunction> function = [library newFunctionWithName:@"spk_write"];
        if (!function) return @"metal4_compute: FAIL_SHADER";
        id<MTLComputePipelineState> pipeline = [device newComputePipelineStateWithFunction:function error:&error];
        if (!pipeline) return @"metal4_compute: FAIL_PIPELINE";
        id<MTLBuffer> output = [device newBufferWithLength:16 options:MTLResourceStorageModeShared];
        if (!output) return @"metal4_compute: FAIL_BUFFER";
        ((uint32_t *)output.contents)[0] = 0;
        MTL4CommandQueueDescriptor *qd = [MTL4CommandQueueDescriptor new];
        qd.feedbackQueue = dispatch_get_global_queue(QOS_CLASS_UTILITY, 0);
        id<MTL4CommandQueue> queue = [device newMTL4CommandQueueWithDescriptor:qd error:&error];
        if (!queue) return @"metal4_compute: FAIL_QUEUE";
        id<MTL4CommandAllocator> allocator = [device newCommandAllocatorWithDescriptor:[MTL4CommandAllocatorDescriptor new] error:&error];
        id<MTL4CommandBuffer> cb = [device newCommandBuffer];
        MTL4ArgumentTableDescriptor *td = [MTL4ArgumentTableDescriptor new];
        td.maxBufferBindCount = 1;
        id<MTL4ArgumentTable> table = [device newArgumentTableWithDescriptor:td error:&error];
        if (!allocator || !cb || !table) return @"metal4_compute: FAIL_SETUP";
        [table setAddress:output.gpuAddress atIndex:0];
        [cb beginCommandBufferWithAllocator:allocator];
        id<MTL4ComputeCommandEncoder> encoder = [cb computeCommandEncoder];
        [encoder setComputePipelineState:pipeline];
        [encoder setArgumentTable:table];
        [encoder dispatchThreadgroups:MTLSizeMake(1,1,1) threadsPerThreadgroup:MTLSizeMake(1,1,1)];
        [encoder endEncoding];
        [cb endCommandBuffer];
        dispatch_semaphore_t done = dispatch_semaphore_create(0);
        MTL4CommitOptions *options = [MTL4CommitOptions new];
        [options addFeedbackHandler:^(id<MTL4CommitFeedback> feedback) {
            (void)feedback;
            dispatch_semaphore_signal(done);
        }];
        id<MTL4CommandBuffer> buffers[] = { cb };
        [queue commit:buffers count:1 options:options];
        if (dispatch_semaphore_wait(done, dispatch_time(DISPATCH_TIME_NOW, 3 * NSEC_PER_SEC)) != 0)
            return @"metal4_compute: TIMEOUT";
        return ((uint32_t *)output.contents)[0] == 0x1234ABCDu
            ? @"metal4_compute: OUTPUT_VERIFIED"
            : @"metal4_compute: WRONG_OUTPUT";
    }
    return @"metal4_compute: UNSUPPORTED_OS";
#endif
}
