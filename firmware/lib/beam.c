#include "beam.h"

#include <math.h>
#include <string.h>

#define C0 299792458.0f
#define PI_F 3.14159265358979f

void beam_default_cfg(beam_cfg_t *cfg)
{
    memset(cfg, 0, sizeof *cfg);
    cfg->freq_hz = 24.125e9f;
    cfg->dx_m = 5.6e-3f;
    cfg->dy_m = 4.6e-3f;
    cfg->phase_bits = 6;
    cfg->taper = 0;
}

/* Direction cosines for az/el measured from boresight (z axis): u along x (right), v along y (up). */
static int direction(float az_deg, float el_deg, float *u, float *v)
{
    const float az = az_deg * PI_F / 180.0f, el = el_deg * PI_F / 180.0f;
    *u = cosf(el) * sinf(az);
    *v = sinf(el);
    return (*u * *u + *v * *v <= 1.0f + 1e-6f) && fabsf(az_deg) < 90.0f && fabsf(el_deg) < 90.0f ? 0 : -1;
}

static float taper_1d(int i, int n)
{
    /* Hann on a 0.3 pedestal: about -23 dB first sidelobe for 8 elements, ~1 dB taper loss */
    const float t = (i + 0.5f) / (float)n;
    return 0.3f + 0.7f * 0.5f * (1.0f - cosf(2.0f * PI_F * t));
}

int beam_steer(const beam_cfg_t *cfg, float az_deg, float el_deg, beam_weights_t *out)
{
    float u, v;
    if (direction(az_deg, el_deg, &u, &v) != 0)
        return -1;
    const float k = 2.0f * PI_F * cfg->freq_hz / C0;
    const int levels = 1 << cfg->phase_bits;
    const float step = 360.0f / (float)levels;
    for (int r = 0; r < BEAM_NY; r++) {
        const float y = ((BEAM_NY - 1) * 0.5f - r) * cfg->dy_m;   /* row 0 at the top */
        for (int c = 0; c < BEAM_NX; c++) {
            const int i = r * BEAM_NX + c;
            const float x = (c - (BEAM_NX - 1) * 0.5f) * cfg->dx_m;
            /* progressive phase that cancels the path difference towards (u, v) */
            float ph = -k * (x * u + y * v) * 180.0f / PI_F + cfg->cal_phase_deg[i];
            ph = fmodf(ph, 360.0f);
            if (ph < 0.0f)
                ph += 360.0f;
            out->phase_code[i] = (uint8_t)((int)lrintf(ph / step) % levels);
            out->amplitude[i] = cfg->taper ? taper_1d(r, BEAM_NY) * taper_1d(c, BEAM_NX) : 1.0f;
        }
    }
    return 0;
}

float beam_array_factor(const beam_cfg_t *cfg, const beam_weights_t *w, float az_deg, float el_deg)
{
    float u, v;
    if (direction(az_deg, el_deg, &u, &v) != 0)
        return 0.0f;
    const float k = 2.0f * PI_F * cfg->freq_hz / C0;
    const float step = 2.0f * PI_F / (float)(1 << cfg->phase_bits);
    float re = 0.0f, im = 0.0f, asum = 0.0f;
    for (int r = 0; r < BEAM_NY; r++) {
        const float y = ((BEAM_NY - 1) * 0.5f - r) * cfg->dy_m;
        for (int c = 0; c < BEAM_NX; c++) {
            const int i = r * BEAM_NX + c;
            const float x = (c - (BEAM_NX - 1) * 0.5f) * cfg->dx_m;
            const float ph = k * (x * u + y * v) + w->phase_code[i] * step
                             - cfg->cal_phase_deg[i] * PI_F / 180.0f;
            re += w->amplitude[i] * cosf(ph);
            im += w->amplitude[i] * sinf(ph);
            asum += w->amplitude[i];
        }
    }
    return asum > 0.0f ? sqrtf(re * re + im * im) / asum : 0.0f;
}
