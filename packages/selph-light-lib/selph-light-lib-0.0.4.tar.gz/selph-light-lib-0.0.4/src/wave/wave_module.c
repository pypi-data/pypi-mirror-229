#include <stdlib.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "cie_rgb.h"

PyObject *wave_length_to_rgb(PyObject *self, PyObject *args)
{
    PyObject *result;
    unsigned char *rgb;
    double wave_length;

    if (! PyArg_ParseTuple(args, "d", &wave_length))
        return NULL;

    rgb = wave_length_to_rgb_c(wave_length);
    if (! rgb)
        return NULL;

    result = Py_BuildValue("(iii)", rgb[0], rgb[1], rgb[2]);
    free(rgb);

    return result;
}
