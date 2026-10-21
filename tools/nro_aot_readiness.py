"""Conservative go/no-go checklist for an NRO ahead-of-time iPadOS port.

Aggregates measured static evidence. It does NOT build, sign or execute code.
"""
import json
import argparse
from pathlib import Path
from tools.nro_relocation_map import relocation_map
from tools.nro_direct_cfg import analyze_entry
from tools.nro_svc_sysreg_inventory import inventory
from tools.nro_x18_audit import audit_x18

def assess(blob: bytes) -> dict:
    reloc = relocation_map(blob)
    cfg = analyze_entry(blob)
    sys = inventory(blob)
    x18 = audit_x18(blob)
    blockers = []
    if reloc["has_unmapped_targets"]:
        blockers.append("relocation_targets_outside_segments")
    if reloc["relr_site_count"]:
        blockers.append("guest_relr_relocation_application_unimplemented")
    if cfg["indirect_frontier_count"]:
        blockers.append("indirect_control_flow_unresolved")
    if sys["svc_immediate_counts"]:
        blockers.append("horizon_svc_compatibility_unimplemented")
    if sys["mrs_register_counts"] or sys["msr_register_counts"]:
        blockers.append("system_register_semantics_unverified")
    if x18["recognized_x18_candidates"]:
        blockers.append("apple_reserved_x18_abi_unresolved")
    blockers.extend(["signed_aot_macho_generation_unimplemented",
                     "guest_libnx_bootstrap_unimplemented",
                     "graphics_and_input_bridge_unimplemented"])
    return {
        "schema_version": 1, "target": "iPadOS signed AOT",
        "evidence": {
            "relr_site_count": reloc["relr_site_count"],
            "unmapped_relr_targets": reloc["relr_targets_by_segment"]["unmapped"],
            "candidate_cfg_instructions": cfg["visited_instruction_count"],
            "unresolved_indirect_frontiers": cfg["indirect_frontier_count"],
            "svc_distinct_immediates": len(sys["svc_immediate_counts"]),
            "x18_partial_candidates": x18["recognized_x18_candidates"],
        },
        "blockers": blockers, "ready_to_build_ipa": False,
        "native_gameplay_verified": False,
        "note": "Static counts are candidates; zero matches never proves compatibility.",
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("nro", type=Path)
    args = parser.parse_args()
    path = args.nro
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 256*1024*1024:
        parser.error("expected a local regular NRO up to 256 MiB")
    print(json.dumps(assess(path.read_bytes()), indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
