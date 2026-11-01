# Regulatory notes (24 GHz ISM)

These notes are for engineering planning, not legal advice. Check the current text of the rules for every country
the product will ship to.

- **Band:** 24.00 – 24.25 GHz. Keep the whole FMCW sweep, plus the VCO's temperature drift, inside it. The 200 MHz
  sweep leaves 25 MHz of guard band at each end.
- **EU (ETSI EN 300 440, short-range devices):** the commonly cited limit for 24.00 – 24.25 GHz is
  **100 mW EIRP (20 dBm)**. With about 18 dBi of array gain, the total conducted power into the array must be only
  around **+2 dBm**, so the beamformer transmit path runs far below its maximum.
- **US (FCC Part 15):** §15.249 limits the fundamental to 250 mV/m at 3 m, which works out to about **19 mW EIRP
  (≈ 12.7 dBm)**. §15.245 (field disturbance sensors) allows 2500 mV/m in this band, about 100× more power. Pick the rule section early, because it sets the transmit power and
  the test plan.
- **Beam steering and EIRP:** the limit applies to the peak of the beam. Because the array gain is roughly constant
  over the scan, a fixed transmit-power setting is enough. Verify this at the worst-case scan angle during
  compliance testing.
- **Drone use:** some regions restrict airborne use of short-range-device bands. Check the aviation rules as well as
  the radio rules.
