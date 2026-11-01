#!/usr/bin/env python3
"""FMCW waveform figures and a monostatic radar-equation range estimate.

Planning numbers only; every input is an assumption listed at the top.

    python3 tools/radar_budget.py
"""
import math

C = 299_792_458.0
K_B = 1.380649e-23

# --- assumptions (edit here) -------------------------------------------------
F0 = 24.125e9          # Hz, centre of the 24.00-24.25 GHz ISM band
BW = 200e6             # Hz, sweep bandwidth (inside the 250 MHz band with margin)
T_CHIRP = 128e-6       # s, chirp duration
N_SAMPLES = 256        # ADC samples per chirp
N_CHIRPS = 64          # chirps per frame (Doppler FFT length)
EIRP_DBM = 20.0        # dBm, 100 mW EIRP (ETSI EN 300 440 limit for 24.00-24.25 GHz)
G_RX_DBI = 18.0        # dBi, realised receive array gain (aperture ~21 dBi minus feed/beamformer loss)
NF_DB = 12.0           # dB, receive noise figure including beamformer and T/R losses
L_SYS_DB = 3.0         # dB, radome, processing and misc. losses
SNR_DET_DB = 13.0      # dB, required post-integration SNR (CFAR, Pd ~0.9, Pfa ~1e-6)
TARGETS = {            # m^2, rough RCS at 24 GHz
    'small drone': 0.01,
    'person': 0.5,
    'tree trunk / pole': 1.0,
    'car': 10.0,
}
# -----------------------------------------------------------------------------


def main():
    lam = C / F0
    slope = BW / T_CHIRP
    fs = N_SAMPLES / T_CHIRP
    r_res = C / (2 * BW)
    r_max_if = fs / 2 * C / (2 * slope)          # complex sampling would double this
    t_frame = N_CHIRPS * T_CHIRP
    v_max = lam / (4 * T_CHIRP)
    v_res = lam / (2 * t_frame)
    print(f'lambda = {lam*1e3:.2f} mm, sweep {BW/1e6:.0f} MHz in {T_CHIRP*1e6:.0f} us (slope {slope/1e12:.2f} MHz/us)')
    print(f'ADC rate {fs/1e6:.2f} MSa/s real, range resolution {r_res:.2f} m, IF-limited max range {r_max_if:.0f} m')
    print(f'frame {t_frame*1e3:.1f} ms: v_max +/-{v_max:.1f} m/s, v_res {v_res:.2f} m/s')

    # integration gain: coherent over samples (range FFT) and chirps (Doppler FFT)
    n_int = N_SAMPLES * N_CHIRPS
    b_eff = 1 / (t_frame)                          # noise bandwidth of one range-Doppler cell
    noise_dbm = 10 * math.log10(K_B * 290 * b_eff * 1e3) + NF_DB
    print(f'noise per range-Doppler cell: {noise_dbm:.1f} dBm (B_eff {b_eff:.0f} Hz, NF {NF_DB} dB)')
    for name, rcs in TARGETS.items():
        # Pr = EIRP * Grx * lam^2 * rcs / ((4pi)^3 R^4 L)
        k_db = (EIRP_DBM + G_RX_DBI + 20 * math.log10(lam) + 10 * math.log10(rcs)
                - 30 * math.log10(4 * math.pi) - L_SYS_DB)
        r = 10 ** ((k_db - noise_dbm - SNR_DET_DB) / 40)
        print(f'  detection range, {name:18s} ({rcs:>5} m^2): {r:6.0f} m')
    print(f'(these assume {n_int} coherently integrated samples per frame and a static beam)')


if __name__ == '__main__':
    main()
