# Hardware

No schematic or layout yet. This is the starting proposal.

## Board partitioning

Two boards, both 50 × 40 mm, stacked:

1. **RF board:** the patch array on the front and the beamformer ICs on the back, each beamformer close to the
   elements it feeds. It also carries the combiner network and the 24 GHz transceiver.
2. **Digital board:** MCU, IF ADC (or the MCU's own ADC, if fast and clean enough), power regulation, CAN
   transceiver and two JST-GH 4-pin connectors in the standard DroneCAN pin-out, for daisy-chaining.

A low-profile board-to-board connector carries the IF signal, SPI, control lines and power between the boards.

## RF board stack-up (proposal, 6 layers)

| Layer | Material / role |
|---|---|
| L1 | Patches (top), with the antenna area free of copper pour |
| — | RO4350B 0.254 mm (antenna dielectric) |
| L2 | Solid ground, the patch ground plane |
| — | RO4350B 0.254 mm |
| L3 | 24 GHz feed / combiner network (stripline) |
| — | FR-4 or RO4450F bonding |
| L4 | Ground |
| L5 | Control / SPI / power |
| L6 | Beamformer ICs and the transceiver (bottom), with feed vias to the L1 patches |

**Check with the fabricator:**
- Back-drilled or blind vias for the patch probe feeds; via stubs at 24 GHz are a problem.
- Controlled-depth milling, if the radome mounts directly on the board.
- Rogers / FR-4 hybrid lamination and the tolerances they can hold on 0.254 mm cores.

## Layout files

- `element_positions.csv`: patch centres in mm, board centre at (0, 0), row 0 at the top. Regenerate it with
  `python3 tools/array_calc.py --csv hardware/element_positions.csv` if the pitch changes.
- Patch size from the first-order model: W 4.07 mm (along x) × L 3.16 mm (along y). Final dimensions come from EM
  simulation with the real stack-up and feed.

## Mass and power targets

| | Target |
|---|---|
| Mass (both boards, radome, connectors) | < 25 g |
| Supply | 5 V from the CAN connector |
| Average power | < 3 W scanning (depends on the beamformer choice; see the power section of docs/architecture.md) |
