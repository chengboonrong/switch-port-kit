import Foundation

/// Exercises the signed C host contract in both simulator and physical builds.
/// This is NOT a Horizon SVC test and never executes guest NRO code.
enum HostContractProbe {
    static func run() -> [String] {
        let abi = UInt32(SPK_HOST_ABI_VERSION)
        var ping = SPKHostReply()
        let status = spk_host_dispatch(UInt32(SPK_HOST_PING), 0x1234, &ping)
        let expected: UInt64 = 0x1234 ^ 0x0A17A17A17A17A17
        let pingOK = status == UInt32(SPK_RESULT_OK)
            && ping.abi_version == abi
            && ping.result == UInt32(SPK_RESULT_OK)
            && ping.value == expected

        var unknown = SPKHostReply()
        let unknownStatus = spk_host_dispatch(0x52, 123, &unknown)
        let unknownOK = unknownStatus == UInt32(SPK_RESULT_NOT_IMPLEMENTED)
            && unknown.abi_version == abi
            && unknown.result == UInt32(SPK_RESULT_NOT_IMPLEMENTED)
            && unknown.value == 0

        // Bracket the host reply with the same Darwin clock read directly,
        // so the value is proven to be CLOCK_MONOTONIC in nanoseconds.
        var t0 = SPKHostReply()
        var t1 = SPKHostReply()
        let before = clock_gettime_nsec_np(CLOCK_MONOTONIC)
        let clock0 = spk_host_dispatch(UInt32(SPK_HOST_MONOTONIC_NANOS), 0, &t0)
        let clock1 = spk_host_dispatch(UInt32(SPK_HOST_MONOTONIC_NANOS), 0, &t1)
        let after = clock_gettime_nsec_np(CLOCK_MONOTONIC)
        let clockOK = clock0 == UInt32(SPK_RESULT_OK)
            && clock1 == UInt32(SPK_RESULT_OK)
            && t0.abi_version == abi && t1.abi_version == abi
            && before > 0 && before <= t0.value && t0.value <= t1.value && t1.value <= after

        var reserved = SPKHostReply()
        let reservedStatus = spk_host_dispatch(UInt32(SPK_HOST_MONOTONIC_NANOS), 1, &reserved)
        let reservedOK = reservedStatus == UInt32(SPK_RESULT_INVALID_ARGUMENT)
            && reserved.abi_version == abi
            && reserved.result == UInt32(SPK_RESULT_INVALID_ARGUMENT)
            && reserved.value == 0

        return [
            "host_contract_ping: \(pingOK ? "PASS" : "FAIL")",
            "host_contract_unknown_request: \(unknownOK ? "PASS" : "FAIL")",
            "host_contract_monotonic_clock: \(clockOK ? "PASS" : "FAIL")",
            "host_contract_reserved_argument: \(reservedOK ? "PASS" : "FAIL")",
            "host_contract_scope: HOST_ONLY_NOT_HORIZON"
        ]
    }
}
