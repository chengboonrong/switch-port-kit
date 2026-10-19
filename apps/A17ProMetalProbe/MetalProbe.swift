import Foundation
import Metal
import UIKit

enum MetalProbe {
    static func run() -> String {
        #if targetEnvironment(simulator)
        // Simulator GPU capabilities do not represent a physical A17 Pro.
        // Keep this path deterministic for UI tests; run hardware probes only on device.
        return [
            "SwitchPortKit Metal Capability Report",
            "execution_environment: simulator",
            "hardware_probes: SKIPPED",
            "note: Physical iPad mini A17 Pro required for BC texture validation."
        ].joined(separator: "\n")
        #else
        guard let device = MTLCreateSystemDefaultDevice() else {
            return "ERROR: Metal device unavailable."
        }
        var lines = [
            "SwitchPortKit Metal Capability Report",
            "timestamp: \(ISO8601DateFormatter().string(from: Date()))",
            "device_model: \(UIDevice.current.model)",
            "os: \(UIDevice.current.systemName) \(UIDevice.current.systemVersion)",
            "metal_device: \(device.name)",
            "apple9_family: \(device.supportsFamily(.apple9))",
            "apple8_family: \(device.supportsFamily(.apple8))",
            "bc_texture_compression: \(device.supportsBCTextureCompression)",
            "max_buffer_length_bytes: \(device.maxBufferLength)",
            "recommended_working_set_bytes: \(device.recommendedMaxWorkingSetSize)"
        ]
        for entry in [(MTLPixelFormat.bc1_rgba, "BC1"), (.bc3_rgba, "BC3"), (.bc7_rgbaUnorm, "BC7")] {
            let descriptor = MTLTextureDescriptor.texture2DDescriptor(
                pixelFormat: entry.0, width: 4, height: 4, mipmapped: false
            )
            descriptor.usage = [.shaderRead]
            descriptor.storageMode = .private
            let texture = device.makeTexture(descriptor: descriptor)
            lines.append("\(entry.1)_texture_allocation: \(texture == nil ? "FAILED" : "OK")")
        }
        lines.append(contentsOf: BCTextureSamplingProbe.run(device: device))
        let queue = device.makeCommandQueue()
        lines.append("command_queue: \(queue == nil ? "FAILED" : "OK")")
        lines.append("note: BC1/BC3 sampling tests compare GPU readback against known red fixtures; BC7 sampling is not yet tested.")
        return lines.joined(separator: "\n")
        #endif
    }
}
