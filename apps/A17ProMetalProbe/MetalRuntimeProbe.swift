import Foundation
import Metal

/// Game-free feature inventory plus a real command submission smoke test.
/// The submission below uses classic Metal intentionally; it does NOT prove
/// nxnative's Metal 4 replay path works.
enum MetalRuntimeProbe {
    static func run(device: MTLDevice) -> [String] {
        var lines: [String] = []
        if #available(iOS 26.0, *) {
            lines.append("metal4_api_os_available: true")
            for name in ["MTL4CommandQueue", "MTL4CommandBuffer",
                         "MTL4CommandAllocator", "MTL4ArgumentTable"] {
                lines.append("\(name)_protocol_present: \(NSProtocolFromString(name) != nil)")
            }
        } else {
            lines.append("metal4_api_os_available: false")
        }

        guard let queue = device.makeCommandQueue(),
              let buffer = device.makeBuffer(length: 64, options: .storageModeShared),
              let command = queue.makeCommandBuffer(),
              let blit = command.makeBlitCommandEncoder() else {
            lines.append("classic_metal_command_submit: FAIL (setup)")
            return lines
        }
        memset(buffer.contents(), 0, 64)
        blit.fill(buffer: buffer, range: NSRange(location: 0, length: 64), value: 0x5A)
        blit.endEncoding()
        command.commit()
        command.waitUntilCompleted()
        let bytes = buffer.contents().assumingMemoryBound(to: UInt8.self)
        let valid = (0..<64).allSatisfy { bytes[$0] == 0x5A }
        lines.append("classic_metal_command_submit: \(command.status == .completed && valid ? "PASS" : "FAIL")")
        lines.append("metal4_command_submit: NOT_TESTED")
        return lines
    }
}
