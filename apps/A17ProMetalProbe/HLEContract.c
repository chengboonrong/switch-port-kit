#define _POSIX_C_SOURCE 200809L
#include "HLEContract.h"
#include <time.h>

uint32_t spk_host_dispatch(uint32_t request, uint64_t argument, SPKHostReply *reply) {
    if (reply == 0) {
        return SPK_RESULT_INVALID_ARGUMENT;
    }
    reply->abi_version = SPK_HOST_ABI_VERSION;
    reply->value = 0;
    reply->result = SPK_RESULT_NOT_IMPLEMENTED;
    if (request == SPK_HOST_PING) {
        // Deterministic host-only smoke operation; not an emulated Switch service.
        reply->value = argument ^ UINT64_C(0xA17A17A17A17A17);
        reply->result = SPK_RESULT_OK;
    }
    if (request == SPK_HOST_MONOTONIC_NANOS) {
        if (argument != 0) {
            reply->result = SPK_RESULT_INVALID_ARGUMENT;
            return reply->result;
        }
        struct timespec now;
        if (clock_gettime(CLOCK_MONOTONIC, &now) == 0 &&
            now.tv_sec >= 0 && now.tv_nsec >= 0 && now.tv_nsec < 1000000000L) {
            reply->value = (uint64_t)now.tv_sec * UINT64_C(1000000000) + (uint64_t)now.tv_nsec;
            reply->result = SPK_RESULT_OK;
        }
    }
    return reply->result;
}
