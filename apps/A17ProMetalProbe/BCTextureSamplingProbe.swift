import Foundation
import Metal

/// Uploads known 4x4 BC blocks, samples in a compute shader and checks pixel values.
/// No game assets or encryption keys are required.
enum BCTextureSamplingProbe {
    private static let shader = """
    #include <metal_stdlib>
    using namespace metal;
    kernel void sampleBC(texture2d<float, access::sample> tex [[texture(0)]],
                         device float4* out [[buffer(0)]],
                         uint id [[thread_position_in_grid]]) {
        if (id != 0) return;
        constexpr sampler s(coord::normalized, address::clamp_to_edge,
                            filter::nearest);
        out[0] = tex.sample(s, float2(0.5, 0.5));
    }
    """

    static func run(device: MTLDevice) -> [String] {
        guard device.supportsBCTextureCompression else {
            return ["BC1_sampling: SKIPPED", "BC3_sampling: SKIPPED"]
        }
        do {
            let library = try device.makeLibrary(source: shader, options: nil)
            guard let function = library.makeFunction(name: "sampleBC") else {
                return ["BC_sampling_error: missing shader function"]
            }
            let pipeline = try device.makeComputePipelineState(function: function)
            return [
                sample(device: device, pipeline: pipeline, name: "BC1",
                       pixelFormat: .bc1_rgba,
                       block: [0x00, 0xf8, 0x00, 0xf8, 0, 0, 0, 0]),
                sample(device: device, pipeline: pipeline, name: "BC3",
                       pixelFormat: .bc3_rgba,
                       block: [255, 255, 0, 0, 0, 0, 0, 0,
                               0x00, 0xf8, 0x00, 0xf8, 0, 0, 0, 0])
            ]
        } catch {
            return ["BC_sampling_error: \(error.localizedDescription)"]
        }
    }

    private static func sample(device: MTLDevice,
                               pipeline: MTLComputePipelineState,
                               name: String,
                               pixelFormat: MTLPixelFormat,
                               block: [UInt8]) -> String {
        let descriptor = MTLTextureDescriptor.texture2DDescriptor(
            pixelFormat: pixelFormat, width: 4, height: 4, mipmapped: false)
        descriptor.usage = [.shaderRead]
        descriptor.storageMode = .private
        guard let texture = device.makeTexture(descriptor: descriptor),
              let source = device.makeBuffer(length: block.count, options: .storageModeShared),
              let output = device.makeBuffer(length: MemoryLayout<Float>.size * 4,
                                              options: .storageModeShared),
              let queue = device.makeCommandQueue(),
              let command = queue.makeCommandBuffer(),
              let blit = command.makeBlitCommandEncoder() else {
            return "\(name)_sampling: FAILED (resource allocation)"
        }

        block.withUnsafeBytes { raw in
            guard let base = raw.baseAddress else { return }
            memcpy(source.contents(), base, block.count)
        }
        blit.copy(from: source, sourceOffset: 0,
                  sourceBytesPerRow: block.count,
                  sourceBytesPerImage: block.count,
                  sourceSize: MTLSize(width: 4, height: 4, depth: 1),
                  to: texture, destinationSlice: 0, destinationLevel: 0,
                  destinationOrigin: MTLOrigin(x: 0, y: 0, z: 0))
        blit.endEncoding()

        guard let compute = command.makeComputeCommandEncoder() else {
            return "\(name)_sampling: FAILED (compute encoder)"
        }
        compute.setComputePipelineState(pipeline)
        compute.setTexture(texture, index: 0)
        compute.setBuffer(output, offset: 0, index: 0)
        compute.dispatchThreads(MTLSize(width: 1, height: 1, depth: 1),
                                threadsPerThreadgroup: MTLSize(width: 1, height: 1, depth: 1))
        compute.endEncoding()
        command.commit()
        command.waitUntilCompleted()
        guard command.status == .completed else {
            return "\(name)_sampling: FAILED (command status \(command.status.rawValue))"
        }
        let rgba = output.contents().bindMemory(to: Float.self, capacity: 4)
        // Both fixtures encode opaque red (BC1 color 565 0xf800, BC3 alpha 255).
        let ok = abs(rgba[0] - 1) < 0.02 && abs(rgba[1]) < 0.02 &&
                 abs(rgba[2]) < 0.02 && abs(rgba[3] - 1) < 0.02
        let value = (0..<4).map { String(format: "%.3f", rgba[$0]) }.joined(separator: ",")
        return "\(name)_sampling: \(ok ? "PASS" : "FAIL") (rgba=\(value))"
    }
}
