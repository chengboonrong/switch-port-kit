# nxnative runtime gate inventory

```sh
python3 tools/runtime_gates.py --nxnative ~/nxnative
```

Reports whether selected known requirements occur in the current checkout: iOS 26, A18 compilation, universal iPhone/iPad target, embedded NSO module flow and BC compression. These are **source matches, not compatibility conclusions**. The result deliberately never marks A17 Pro as supported.

The crucial unanswered question is whether compilation targeting Apple A18 produces instructions or assumptions incompatible with A17 Pro. Actual disassembly and hardware validation are required. Separately, Metal 4 symbols require capability-by-capability checks rather than a blanket iOS version assumption.

This does not consume game files, title IDs, copyrighted binaries, firmware or keys.
