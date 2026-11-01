# Array design

All numbers come from `python3 tools/array_calc.py` (uniform weights; the element pattern is approximated as cos¹·⁵).
They are planning figures. Confirm them with an EM solver before layout.

## Fitting 8 × 8 elements on 50 × 40 mm

At 24.125 GHz, λ₀ = 12.43 mm, so the textbook λ/2 pitch is 6.21 mm. Eight columns at λ/2 span 43.5 mm (patch
centres), which fits the 50 mm side. **Eight rows at λ/2 would need ~50 mm and do not fit the 40 mm side.** The
chosen pitch is:

| Axis | Pitch | In wavelengths | Element span | Edge clearance (board edge to patch edge) |
|---|---|---|---|---|
| x, azimuth (50 mm side) | 5.6 mm | 0.451 λ | 39.2 mm | 3.4 mm |
| y, elevation (40 mm side) | 4.6 mm | 0.370 λ | 32.2 mm | 2.3 mm |

What the sub-λ/2 pitch does:

- **Good:** no grating lobes at any scan angle, because a pitch below λ/2 can scan to ±90° without one.
- **Cost:** the effective aperture in elevation is smaller, so the elevation beam is wider (17° vs. 14° in azimuth).
- **Cost:** stronger mutual coupling between rows (only a 1.4 mm gap). This shifts the element match with scan angle,
  so active-impedance simulation and per-element calibration are mandatory, not optional.

## Patch element

Rectangular patch on Rogers RO4350B (εr 3.66, 0.254 mm / 10 mil), transmission-line model:
**W ≈ 4.07 mm, L ≈ 3.16 mm** (εeff ≈ 3.34). The width runs along x, the resonant length along y.

- **Feed:** a probe (via) from the beamformer layer underneath, which keeps the top layer free of feed lines.
  The gaps (1.53 mm in x, 1.44 mm in y) leave no room for inset microstrip feeds between patches.
- **Bandwidth:** only 250 MHz (about 1 %) is needed, which a thin patch covers easily.
- **Polarisation:** linear. The resonant length runs along y, so the polarisation is vertical when the long
  50 mm side is horizontal.

## Beam figures

| Scan | Azimuth HPBW | Elevation HPBW |
|---|---|---|
| 0° | 14.1° | 17.1° |
| 30° | 16.3° | 19.8° |
| 45° | 19.9° | 24.2° |
| 60° | 28.2° | 34.3° |

- **Directivity:** ~21.3 dBi from the aperture. Allowing about 3 dB for beamformer, feed and radome loss gives
  **~18 dBi realised**, which is the value `tools/radar_budget.py` uses.
- **Sidelobes:** −13 dB first sidelobe with uniform weights. At 45° scan the element pattern raises them to about
  −9 dB and pulls the peak about 3° back towards broadside. The beam controller should apply this correction, or
  the scan table should be generated from measured patterns.
- **Taper:** with a gain-controlled beamformer, the separable Hann-on-pedestal taper in `beam.c` brings the first
  sidelobe to about −25 dB, for roughly 1 dB of taper loss. The unit test checks this.

## Phase quantisation and calibration

- **Quantisation:** 6-bit phase shifters (5.625° steps) keep pointing error under 1° and quantisation loss under
  0.1 dB across ±60°. This is checked by `firmware/test/test_beam.c`.
- **Calibration:** each element's phase offset (feed-length differences, IC channel mismatch) is stored as
  `cal_phase_deg[]` and added before quantising.
- **Measuring the offsets:** use a near-field or compact-range measurement with a reference horn. As a
  lower-precision in-field alternative, toggle each element by 180° against a fixed corner reflector and fit the
  phases.

Element positions for layout: [`hardware/element_positions.csv`](../hardware/element_positions.csv). Coordinates are
in mm with the board centre at (0, 0); row 0 is the top row.
