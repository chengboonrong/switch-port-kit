#include "HLEContract.h"

uint32_t spk_host_dispatch(uint32_t request, uint64_t argument, SPKHostReply *reply) {
    if (reply == 0) {
        return SPK_RESULT_INVALID_ARGUMENT;
    }
    reply->abi_version = 1;
    reply->value = 0;
    reply->result = SPK_RESULT_NOT_IMPLEMENTED;
    if (request == SPK_HOST_PING) {
        // Deterministic host-only smoke operation; not an emulated Switch service.
        reply->value = argument ^ UINT64_C(0xA17A17A17A17A17);
        reply->result = SPK_RESULT_OK;
    }
    return reply->result;
}
