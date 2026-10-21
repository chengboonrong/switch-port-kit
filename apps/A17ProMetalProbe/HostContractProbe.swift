import Foundation

/// Exercises the signed C host contract in both simulator and physical builds.
/// This is NOT a Horizon SVC test and never executes guest NRO code.
enum HostContractProbe {
    static func run() -> [String] {
        var ping = SPKHostReply()
        let status = spk_host_dispatch(UInt32(SPK_HOST_PING), 0x1234, &ping)
        let expected: UInt64 = 0x1234 ^ 0x0A17A17A17A17A17
        let pingOK = status == UInt32(SPK_RESULT_OK)
            && ping.abi_version == 1
            && ping.result == UInt32(SPK_RESULT_OK)
            && ping.value == expected

        var unknown = SPKHostReply()
        let unknownStatus = spk_host_dispatch(0x52, 123, &unknown)
        let unknownOK = unknownStatus == UInt32(SPK_RESULT_NOT_IMPLEMENTED)
            && unknown.abi_version == 1
            && unknown.result == UInt32(SPK_RESULT_NOT_IMPLEMENTED)
            && unknown.value == 0

        var t0 = SPKHostReply()
        var t1 = SPKHostReply()
        let clock0 = spk_host_dispatch(UInt32(SPK_HOST_MONOTONIC_NANOS), 0, &t0)
        let clock1 = spk_host_dispatch(UInt32(SPK_HOST_MONOTONIC_NANOS), 0, &t1)
        let clockOK = clock0 == UInt32(SPK_RESULT_OK)
            && clock1 == UInt32(SPK_RESULT_OK)
            && t0.value > 0 && t1.value >= t0.value

        return [
            "host_contract_ping: \(pingOK ? "PASS" : "FAIL")",
            "host_contract_unknown_request: \(unknownOK ? "PASS" : "FAIL")",
            "host_contract_monotonic_clock: \(clockOK ? "PASS" : "FAIL")",
            "host_contract_scope: HOST_ONLY_NOT_HORIZON"
        ]
    }
}
