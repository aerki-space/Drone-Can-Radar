/*
 * Beam steering for the 8x8 array: per-element phase (and optional amplitude taper)
 * for a requested azimuth/elevation, quantised to the phase-shifter resolution.
 * Pure C99, no hardware dependencies, so it builds and tests on the host.
 */
#ifndef BEAM_H
#define BEAM_H

#include <stdint.h>

#define BEAM_NX 8
#define BEAM_NY 8
#define BEAM_N  (BEAM_NX * BEAM_NY)

typedef struct {
    float freq_hz;          /* carrier, e.g. 24.125e9 */
    float dx_m, dy_m;       /* element pitch along x (azimuth) and y (elevation) */
    uint8_t phase_bits;     /* phase-shifter resolution, e.g. 6 -> 5.625 deg steps */
    uint8_t taper;          /* 0 = uniform, 1 = separable Hann-on-pedestal taper */
    float cal_phase_deg[BEAM_N]; /* per-element phase calibration offsets, added before quantising */
} beam_cfg_t;

typedef struct {
    uint8_t phase_code[BEAM_N]; /* 0 .. 2^phase_bits - 1, element index = row * BEAM_NX + col */
    float amplitude[BEAM_N];    /* linear, 0..1 (only meaningful with a gain-controlled beamformer) */
} beam_weights_t;

/* Fill cfg with the board defaults (24.125 GHz, 5.6 x 4.6 mm pitch, 6-bit, uniform, zero calibration). */
void beam_default_cfg(beam_cfg_t *cfg);

/*
 * Steer to azimuth az_deg (positive = right) and elevation el_deg (positive = up), both measured
 * from boresight. Row 0 is the top row, column 0 the left column, seen from the front of the array.
 * Returns 0 on success, -1 if the direction is outside the visible hemisphere.
 */
int beam_steer(const beam_cfg_t *cfg, float az_deg, float el_deg, beam_weights_t *out);

/* Normalised array-factor magnitude (0..1) of weights w towards (az_deg, el_deg); used by tests/calibration. */
float beam_array_factor(const beam_cfg_t *cfg, const beam_weights_t *w, float az_deg, float el_deg);

#endif
