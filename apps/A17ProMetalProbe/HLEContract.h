#ifndef SPK_HLE_CONTRACT_H
#define SPK_HLE_CONTRACT_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

// Host-only test protocol. These IDs are NOT Nintendo Horizon SVC numbers.
enum {
    SPK_HOST_ABI_VERSION = 1
};
enum {
    SPK_HOST_PING = 1,
    SPK_HOST_MONOTONIC_NANOS = 2, // argument is reserved and must be 0
    SPK_HOST_UNIMPLEMENTED = 0xFFFFFFFFu
};
enum {
    SPK_RESULT_OK = 0,
    SPK_RESULT_NOT_IMPLEMENTED = 0xF601,
    SPK_RESULT_INVALID_ARGUMENT = 0xF602,
    SPK_RESULT_HOST_FAILURE = 0xF603
};
typedef struct {
    uint32_t abi_version;
    uint32_t result;
    uint64_t value;
} SPKHostReply;

// Fixed ABI layout: any compiler that disagrees fails to build.
_Static_assert(sizeof(SPKHostReply) == 16, "SPKHostReply must be 16 bytes");
_Static_assert(offsetof(SPKHostReply, abi_version) == 0, "abi_version at 0");
_Static_assert(offsetof(SPKHostReply, result) == 4, "result at 4");
_Static_assert(offsetof(SPKHostReply, value) == 8, "value at 8");

uint32_t spk_host_dispatch(uint32_t request, uint64_t argument, SPKHostReply *reply);
#ifdef __cplusplus
}
#endif
#endif
