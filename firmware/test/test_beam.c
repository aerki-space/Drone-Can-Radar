/* Host tests for lib/beam.c:  make -C firmware test */
#include "beam.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

static int failures;
#define CHECK(cond, ...) do { if (!(cond)) { failures++; printf("FAIL %s:%d: ", __FILE__, __LINE__); printf(__VA_ARGS__); printf("\n"); } } while (0)

/* Scan a 2-D grid and return the direction of the strongest array-factor response. */
static void find_peak(const beam_cfg_t *cfg, const beam_weights_t *w, float *az, float *el, float *mag)
{
    *mag = -1.0f;
    for (float a = -80.0f; a <= 80.0f; a += 0.5f)
        for (float e = -80.0f; e <= 80.0f; e += 0.5f) {
            const float m = beam_array_factor(cfg, w, a, e);
            if (m > *mag) { *mag = m; *az = a; *el = e; }
        }
}

static void test_broadside_is_uniform_phase(void)
{
    beam_cfg_t cfg; beam_weights_t w;
    beam_default_cfg(&cfg);
    CHECK(beam_steer(&cfg, 0, 0, &w) == 0, "steer failed");
    for (int i = 0; i < BEAM_N; i++)
        CHECK(w.phase_code[i] == w.phase_code[0], "element %d code %d != %d", i, w.phase_code[i], w.phase_code[0]);
    CHECK(fabsf(beam_array_factor(&cfg, &w, 0, 0) - 1.0f) < 1e-4f, "broadside gain not unity");
}

static void test_peak_follows_steer(void)
{
    const float dirs[][2] = { {30, 0}, {-45, 0}, {0, 20}, {25, -15}, {-50, 30}, {60, 0} };
    beam_cfg_t cfg; beam_weights_t w;
    beam_default_cfg(&cfg);
    for (unsigned d = 0; d < sizeof dirs / sizeof dirs[0]; d++) {
        float az = 0, el = 0, mag;
        CHECK(beam_steer(&cfg, dirs[d][0], dirs[d][1], &w) == 0, "steer failed");
        find_peak(&cfg, &w, &az, &el, &mag);
        /* 6-bit quantisation moves the peak by well under one degree */
        CHECK(fabsf(az - dirs[d][0]) <= 1.0f && fabsf(el - dirs[d][1]) <= 1.0f,
              "asked (%.0f,%.0f) got peak (%.1f,%.1f)", dirs[d][0], dirs[d][1], az, el);
        CHECK(mag > 0.98f, "quantisation loss too high at (%.0f,%.0f): %.3f", dirs[d][0], dirs[d][1], mag);
    }
}

static void test_calibration_is_compensated(void)
{
    beam_cfg_t cfg; beam_weights_t w;
    beam_default_cfg(&cfg);
    srand(1);
    for (int i = 0; i < BEAM_N; i++)
        cfg.cal_phase_deg[i] = (float)(rand() % 360);   /* e.g. unequal feed-line lengths */
    beam_steer(&cfg, 20, 10, &w);
    CHECK(beam_array_factor(&cfg, &w, 20, 10) > 0.98f, "calibration offsets not compensated");
}

static void test_taper_lowers_sidelobes(void)
{
    beam_cfg_t cfg; beam_weights_t w;
    beam_default_cfg(&cfg);
    float worst[2];
    for (int t = 0; t < 2; t++) {
        cfg.taper = (uint8_t)t;
        beam_steer(&cfg, 0, 0, &w);
        /* walk out of the main lobe to its first null, then take the highest response beyond it */
        float a = 0.0f, prev = beam_array_factor(&cfg, &w, 0, 0), cur;
        while (a < 85.0f && (cur = beam_array_factor(&cfg, &w, a + 0.25f, 0)) <= prev) { prev = cur; a += 0.25f; }
        worst[t] = 0.0f;
        for (; a <= 85.0f; a += 0.25f)
            worst[t] = fmaxf(worst[t], beam_array_factor(&cfg, &w, a, 0));
    }
    const float sll_u = 20 * log10f(worst[0]), sll_t = 20 * log10f(worst[1]);
    CHECK(sll_u > -14.5f && sll_u < -12.5f, "uniform sidelobe %.1f dB, expected about -13", sll_u);
    CHECK(sll_t < sll_u - 6.0f, "taper sidelobe %.1f dB not well below uniform %.1f dB", sll_t, sll_u);
}

static void test_rejects_invalid_direction(void)
{
    beam_cfg_t cfg; beam_weights_t w;
    beam_default_cfg(&cfg);
    CHECK(beam_steer(&cfg, 95, 0, &w) == -1, "accepted az beyond 90 deg");
}

int main(void)
{
    test_broadside_is_uniform_phase();
    test_peak_follows_steer();
    test_calibration_is_compensated();
    test_taper_lowers_sidelobes();
    test_rejects_invalid_direction();
    printf(failures ? "%d failure(s)\n" : "all beam tests passed\n", failures);
    return failures != 0;
}
