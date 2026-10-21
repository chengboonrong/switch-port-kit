#ifndef SPK_HLE_CONTRACT_H
#define SPK_HLE_CONTRACT_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

// Host-only test protocol. These IDs are NOT Nintendo Horizon SVC numbers.
enum {
    SPK_HOST_PING = 1,
    SPK_HOST_UNIMPLEMENTED = 0xFFFFFFFFu
};
enum {
    SPK_RESULT_OK = 0,
    SPK_RESULT_NOT_IMPLEMENTED = 0xF601,
    SPK_RESULT_INVALID_ARGUMENT = 0xF602
};
typedef struct {
    uint32_t abi_version;
    uint32_t result;
    uint64_t value;
} SPKHostReply;

uint32_t spk_host_dispatch(uint32_t request, uint64_t argument, SPKHostReply *reply);
#ifdef __cplusplus
}
#endif
#endif
