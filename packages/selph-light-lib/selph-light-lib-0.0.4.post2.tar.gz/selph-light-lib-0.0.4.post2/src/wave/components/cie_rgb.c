#include <math.h>
#include <stdlib.h>

static double *cie1931_to_xyz(double wave_length);
static unsigned char *xyz_to_srgb(const double *xyz);
static double strip_color(double color);

unsigned char *wave_length_to_rgb_c(double wave_length)
{
    unsigned char *rgb;
    double *xyz;

    xyz = cie1931_to_xyz(wave_length);
    rgb = xyz_to_srgb(xyz);
    free(xyz);

    return rgb;
}

static double *cie1931_to_xyz(double wave_length)
{
    double t1, t2, t3, *result = malloc(3 * sizeof(double));

    t1 = (wave_length - 442.0) * ((wave_length < 442.0) ? 0.0624 : 0.0374);
    t2 = (wave_length - 599.8) * ((wave_length < 599.8) ? 0.0264 : 0.0323);
    t3 = (wave_length - 501.1) * ((wave_length < 501.1) ? 0.0490 : 0.0382);
    result[0] = 0.362 * exp(-0.5 * t1 * t1) + 1.056 * exp(-0.5 * t2 * t2) - 0.065 * exp(-0.5 * t3 * t3);


    t1 = (wave_length - 568.8) * ((wave_length < 568.8) ? 0.0213 : 0.0247);
    t2 = (wave_length - 530.9) * ((wave_length < 530.9) ? 0.0613 : 0.0322);
    result[1] = 0.821 * exp(-0.5 * t1 * t1) + 0.286 * exp(-0.5 * t2 * t2);

    t1 = (wave_length - 437.0) * ((wave_length < 437.0) ? 0.0845 : 0.0278);
    t2 = (wave_length - 459.0) * ((wave_length < 459.0) ? 0.0385 : 0.0725);
    result[2] = 1.217 * exp(-0.5 * t1 * t1) + 0.681 * exp(-0.5 * t2 * t2);

    return result;
}

static unsigned char *xyz_to_srgb(const double *xyz)
{
    unsigned char *result = malloc(3 * sizeof(char));
    double x = xyz[0], y = xyz[1], z = xyz[2];

    result[0] = round(strip_color(3.2406255 * x + -1.537208  * y + -0.4986286 * z) * 255);
    result[1] = round(strip_color(-0.9689307 * x + 1.8757561 * y + 0.0415175 * z) * 255);
    result[2] = round(strip_color(0.0557101 * x + -0.2040211 * y + 1.0569959 * z) * 255);

    return result;
}

static double strip_color(double color)
{
    color = color > 1 ? 1 : (color < 0 ? 0 : color);

    return color <= 0.0031308 ? color * 12.92 : 1.055 * pow(color, 1.0 / 2.4) - 0.055;
}
