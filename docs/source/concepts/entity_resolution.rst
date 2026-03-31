Concept: Entity Resolution
==========================

T-code scripts are intended to be robust to change in labware, robot count, pipette tip brand, and various other factors that may change between fleets. As such, T-code scripts are written to operate on ``Descriptors`` (or minimal descriptions) of important entities. At runtime, these ``Descriptors`` are resolved to actual entities (e.g. labware, robots, etc.).

**Goals**:

- Describe how entity resolution works in T-code.
- Provide recipes for common entity resolution tasks.
  - Different pipette tip brands
  - Labware with non-standard well count, spacing, or offset (``GridDescriptor``)
  - Multiple robots
- Describe how to diagnose failing entity resolution.
