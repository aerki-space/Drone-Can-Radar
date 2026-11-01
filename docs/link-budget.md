# Waveform and link budget

From `python3 tools/radar_budget.py`. The assumptions are at the top of that script; change them there, not here.

## Waveform (FMCW, sawtooth)

| Parameter | Value |
|---|---|
| Centre / sweep | 24.125 GHz, 200 MHz in 128 µs (1.56 MHz/µs) |
| ADC | 256 real samples per chirp, 2 MSa/s |
| Range resolution | 0.75 m |
| Max range (IF-limited) | ~96 m with real sampling (complex I/Q sampling or a slower ramp doubles it) |
| Frame | 64 chirps = 8.2 ms per beam position |
| Velocity | ±24.3 m/s unambiguous, 0.76 m/s resolution |

## Detection range

Inputs:
- **Transmit:** 20 dBm EIRP (the ETSI limit, see [regulatory.md](regulatory.md)).
- **Receive:** 18 dBi realised receive gain, 12 dB noise figure, 3 dB system loss.
- **Detection:** 13 dB required SNR, with coherent integration over one frame.

| Target | RCS | Estimated detection range |
|---|---|---|
| Small drone | 0.01 m² | ~63 m |
| Person | 0.5 m² | ~170 m |
| Pole / tree trunk | 1 m² | ~200 m |
| Car | 10 m² | ~355 m |

As configured, the ~96 m IF limit caps everything except the small drone. To use the extra sensitivity, lengthen
the chirp or sample I/Q, at the cost of frame time.

**Caveats:**
- These are single-beam, static figures.
- Clutter, multipath off the ground, and the drone's own propellers (micro-Doppler, close-in returns) will set the
  practical limits more than thermal noise does. Gate out the first 1–2 m of range.
- The EIRP limit is the main lever on range. Range scales with EIRP^¼, so if your jurisdiction allows more, a
  little extra power buys a little more range.
