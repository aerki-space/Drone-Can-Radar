#!/usr/bin/env python3
"""8x8 patch-array geometry and first-order beam figures for the 50 x 40 mm, 24 GHz board.

Pure numpy, no RF solver: these are planning numbers (uniform illumination,
isotropic-element array factor x cos^q element pattern). Confirm with EM simulation.

    python3 tools/array_calc.py              # summary
    python3 tools/array_calc.py --csv out.csv # element positions (mm, board origin = centre)
"""
import argparse
import math

import numpy as np

C = 299_792_458.0


def params(f_hz=24.125e9, nx=8, ny=8, dx_mm=5.6, dy_mm=4.6):
    lam_mm = C / f_hz * 1e3
    return dict(f_hz=f_hz, lam_mm=lam_mm, nx=nx, ny=ny, dx_mm=dx_mm, dy_mm=dy_mm,
                dx_lam=dx_mm / lam_mm, dy_lam=dy_mm / lam_mm)


def patch_size_mm(f_hz, er=3.66, h_mm=0.254):
    """Classic transmission-line model for a rectangular patch (Balanis)."""
    c = C * 1e3
    w = c / (2 * f_hz) * math.sqrt(2 / (er + 1))
    eeff = (er + 1) / 2 + (er - 1) / 2 * (1 + 12 * h_mm / w) ** -0.5
    dl = 0.412 * h_mm * ((eeff + 0.3) * (w / h_mm + 0.264)) / ((eeff - 0.258) * (w / h_mm + 0.8))
    l = c / (2 * f_hz * math.sqrt(eeff)) - 2 * dl
    return w, l, eeff


def positions_mm(p):
    xs = (np.arange(p['nx']) - (p['nx'] - 1) / 2) * p['dx_mm']
    ys = (np.arange(p['ny']) - (p['ny'] - 1) / 2) * p['dy_mm']
    return [(r, c, float(x), float(y)) for r, y in enumerate(ys[::-1]) for c, x in enumerate(xs)]


def max_scan_no_grating(d_lam):
    """Largest scan angle (deg) before a grating lobe enters visible space: d/lambda <= 1/(1+sin th)."""
    v = 1 / d_lam - 1
    return 90.0 if v >= 1 else math.degrees(math.asin(v))


def hpbw_deg(n, d_lam, scan_deg=0.0):
    """Uniform linear array HPBW, broadside approximation broadened by 1/cos(scan)."""
    return math.degrees(0.886 / (n * d_lam)) / math.cos(math.radians(scan_deg))


def array_factor_cut(n, d_lam, scan_deg, q=1.5, npts=3601):
    th = np.linspace(-90, 90, npts)
    k = 2 * np.pi
    psi = k * d_lam * (np.sin(np.radians(th)) - np.sin(np.radians(scan_deg)))
    af = np.abs(np.exp(1j * np.outer(psi, np.arange(n))).sum(1)) / n
    elem = np.cos(np.radians(th)).clip(1e-6) ** q
    return th, 20 * np.log10((af * elem).clip(1e-9))


def directivity_dbi(p):
    ax = p['nx'] * p['dx_mm']
    ay = p['ny'] * p['dy_mm']
    return 10 * math.log10(4 * math.pi * ax * ay / p['lam_mm'] ** 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv')
    a = ap.parse_args()
    p = params()
    w, l, eeff = patch_size_mm(p['f_hz'])
    print(f"f = {p['f_hz']/1e9:.3f} GHz   lambda0 = {p['lam_mm']:.2f} mm   lambda/2 = {p['lam_mm']/2:.2f} mm")
    print(f"patch on RO4350B (er 3.66, h 0.254 mm): W = {w:.2f} mm, L = {l:.2f} mm, eps_eff = {eeff:.2f}")
    print(f"pitch: dx = {p['dx_mm']} mm ({p['dx_lam']:.3f} lambda), dy = {p['dy_mm']} mm ({p['dy_lam']:.3f} lambda)")
    print(f"aperture: {p['nx']*p['dx_mm']:.1f} x {p['ny']*p['dy_mm']:.1f} mm; "
          f"element span {(p['nx']-1)*p['dx_mm']:.1f} x {(p['ny']-1)*p['dy_mm']:.1f} mm on a 50 x 40 mm board")
    print(f"edge clearance (centre-to-edge minus half patch): x {25-(p['nx']-1)*p['dx_mm']/2-w/2:.1f} mm, "
          f"y {20-(p['ny']-1)*p['dy_mm']/2-l/2:.1f} mm")
    print(f"gap between patches: x {p['dx_mm']-w:.2f} mm, y {p['dy_mm']-l:.2f} mm")
    print(f"grating-lobe-free scan: az +/-{max_scan_no_grating(p['dx_lam']):.0f} deg, el +/-{max_scan_no_grating(p['dy_lam']):.0f} deg")
    for s in (0, 30, 45, 60):
        print(f"HPBW at {s:2d} deg scan: az {hpbw_deg(p['nx'], p['dx_lam'], s):.1f} deg, el {hpbw_deg(p['ny'], p['dy_lam'], s):.1f} deg")
    print(f"aperture directivity ~ {directivity_dbi(p):.1f} dBi (uniform, before losses)")
    for s in (0, 45):
        th, g = array_factor_cut(p['nx'], p['dx_lam'], s)
        main = g.max()
        peak_i = int(g.argmax())
        # first sidelobe: highest local max away from the main lobe
        d = np.diff(np.sign(np.diff(g)))
        peaks = [i + 1 for i in np.where(d < 0)[0] if abs(th[i + 1] - th[peak_i]) > hpbw_deg(p['nx'], p['dx_lam'], s)]
        sll = max(g[i] for i in peaks) - main
        print(f"az cut @ {s} deg scan: peak at {th[peak_i]:.1f} deg, highest sidelobe {sll:.1f} dB (uniform weights)")
    if a.csv:
        with open(a.csv, 'w') as fh:
            fh.write('row,col,x_mm,y_mm\n')
            for r, c, x, y in positions_mm(p):
                fh.write(f'{r},{c},{x:.3f},{y:.3f}\n')
        print('wrote', a.csv)


if __name__ == '__main__':
    main()
