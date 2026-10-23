#include "GuestStartup.h"

uint32_t spk_guest_config_build(const SPKGuestStartup *startup, SPKConfigEntry *out,
                                uint32_t capacity, uint32_t *count) {
    if (startup == 0 || count == 0 || startup->main_thread_handle == 0 ||
        (startup->heap_address == 0) != (startup->heap_size == 0)) {
        return SPK_RESULT_INVALID_ARGUMENT;
    }
    uint32_t needed = startup->heap_address ? 3 : 2;
    *count = needed;
    if (out == 0 || capacity < needed) {
        return SPK_RESULT_INVALID_ARGUMENT;
    }
    uint32_t n = 0;
    out[n++] = (SPKConfigEntry){SPK_ENTRY_MAIN_THREAD_HANDLE, 0, {startup->main_thread_handle, 0}};
    if (startup->heap_address) {
        // With a heap override libnx skips svcSetHeapSize and two svcGetInfo calls.
        out[n++] = (SPKConfigEntry){SPK_ENTRY_OVERRIDE_HEAP, 0,
                                    {startup->heap_address, startup->heap_size}};
    }
    // END_OF_LIST value = loader info pointer and size; none.
    out[n++] = (SPKConfigEntry){SPK_ENTRY_END_OF_LIST, 0, {0, 0}};
    return SPK_RESULT_OK;
}
