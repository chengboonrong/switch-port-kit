#ifndef SPK_GUEST_STARTUP_H
#define SPK_GUEST_STARTUP_H
#include "HLEContract.h"
#ifdef __cplusplus
extern "C" {
#endif

// libnx homebrew-ABI loader config, passed to the NRO entry in x0 (x1 = UINT64_MAX).
// Key numbers are libnx's EntryType values, checked against 2048.nro's envSetup;
// see docs/guest-startup-abi.md. Building the list does not execute guest code.
enum {
    SPK_ENTRY_END_OF_LIST = 0,
    SPK_ENTRY_MAIN_THREAD_HANDLE = 1,
    SPK_ENTRY_OVERRIDE_HEAP = 3
};
typedef struct {
    uint32_t key;
    uint32_t flags; // bit 0 = mandatory; never set, so older libnx skips unknown keys
    uint64_t value[2];
} SPKConfigEntry;

_Static_assert(sizeof(SPKConfigEntry) == 24, "SPKConfigEntry must be 24 bytes");
_Static_assert(offsetof(SPKConfigEntry, flags) == 4, "flags at 4");
_Static_assert(offsetof(SPKConfigEntry, value) == 8, "value at 8");

typedef struct {
    uint32_t main_thread_handle; // required: libnx aborts on handle 0 before main
    uint64_t heap_address;       // guest address; 0 with heap_size 0 = no override
    uint64_t heap_size;
} SPKGuestStartup;

// Writes the entries plus END_OF_LIST into out and sets *count.
// If capacity is too small, writes nothing, sets *count to the size needed
// and returns SPK_RESULT_INVALID_ARGUMENT.
uint32_t spk_guest_config_build(const SPKGuestStartup *startup, SPKConfigEntry *out,
                                uint32_t capacity, uint32_t *count);
#ifdef __cplusplus
}
#endif
#endif
