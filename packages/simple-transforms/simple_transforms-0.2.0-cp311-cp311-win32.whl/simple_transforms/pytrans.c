/// @file pyaffine.h 
//
// Copyright (c) 2023, Jef Wagner <jefwagner@gmail.com>
//
// This file is part of simple-transforms.
//
// simple-transforms is free software: you can redistribute it and/or modify it
// under the terms of the GNU General Public License as published by the Free
// Software Foundation, either version 3 of the License, or (at your option) any
// later version.
//
// simple-transforms is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
// details.
//
// You should have received a copy of the GNU General Public License along with
// simple-transforms. If not, see <https://www.gnu.org/licenses/>.
//

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

#include <Python.h>

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>
#include <numpy/ufuncobject.h>

#include <flint.h>
#include <numpy_flint.h>

// Defines so that we can use doubles, floats, and flints with same interface
#define float_inplace_add(A, B) *(A) += B
#define float_multiply(A, B) A * B
#define float_divide(A, B) A / B
#define float_inplace_divide(A, B) *(A) /= B
#define int_to_float(I) (float) I
#define double_inplace_add(A, B) *(A) += B
#define double_multiply(A, B) A * B
#define double_divide(A, B) A / B
#define double_inplace_divide(A, B) *(A) /= B
#define int_to_double(I) (double) I

#define ALMOST_EQUAL_EPS 1.0e-9

PyDoc_STRVAR(apply_vert_docstring, "\
Apply an affine transform to an array of 3-length vertices");

/**
 * Type generic transformation application function macro
 * 
 * :param TYPE: The c type (float, double, flint)
 * :param COMP: The comparison operations
 */
#define PYAFFINE_APPLY_VERT(TYPE, COMP)\
static void pyaffine_apply_vert_##TYPE(char** args,\
                                npy_intp const* dims,\
                                npy_intp const* strides,\
                                void* data) {\
    npy_intp i, j, n;\
    npy_intp N = dims[0];\
    char* af_base = args[0];\
    char* af_i;\
    char* af;\
    char* v_in_base = args[1];\
    char* v_in;\
    char* v_out_base = args[2];\
    char* v_out;\
    npy_intp d_af_n = strides[0];\
    npy_intp d_v_in_n = strides[1];\
    npy_intp d_v_out_n = strides[2];\
    npy_intp d_af_i = strides[3];\
    npy_intp d_af_j = strides[4];\
    npy_intp d_v_in_j = strides[5];\
    npy_intp d_v_out_i = strides[6];\
    TYPE v_in_f, w;\
    for (n=0; n<N; n++) {\
        /* Matrix mult -> v_out = af(:3,:3).v_in */\
        for (i=0; i<3; i++) {\
            af_i = af_base + i*d_af_i;\
            v_out = v_out_base + i*d_v_out_i;\
            *((TYPE*) v_out) = int_to_##TYPE(0);\
            for (j=0; j<3; j++) {\
                af = af_i + j*d_af_j;\
                v_in = v_in_base + j*d_v_in_j;\
                v_in_f = *((TYPE*) v_in);\
                TYPE##_inplace_add((TYPE*) v_out, TYPE##_multiply(*((TYPE*) af), v_in_f));\
            }\
            /* Add trans -> v_out = v_out + af(:3,4) */\
            af = af_i + 3*d_af_j;\
            TYPE##_inplace_add((TYPE*) v_out, *((TYPE*) af));\
        }\
        /* calc homogenous 'w' term */\
        af_i = af_base + 3*d_af_i;\
        w = int_to_##TYPE(0);\
        for (j=0; j<3; j++) {\
            af = af_i + j*d_af_j;\
            v_in = v_in_base + j*d_v_in_j;\
            v_in_f = *((TYPE*) v_in);\
            TYPE##_inplace_add(&w, TYPE##_multiply(*((TYPE*) af), v_in_f));\
        }\
        af = af_i + 3*d_af_j;\
        TYPE##_inplace_add(&w, *((TYPE*) af));\
        /* rescale */\
        if (COMP) {\
            for (i=0; i<3; i++) {\
                v_out = v_out_base + i*d_v_out_i;\
                TYPE##_inplace_divide((TYPE*) v_out, w);\
            }\
        }\
        af_base += d_af_n;\
        v_in_base += d_v_in_n;\
        v_out_base += d_v_out_n;\
    }\
}

PYAFFINE_APPLY_VERT(float, fabs(w-((float) 1.0)) > (float) ALMOST_EQUAL_EPS)
PYAFFINE_APPLY_VERT(double, abs(w - 1.0) > ALMOST_EQUAL_EPS)
PYAFFINE_APPLY_VERT(flint, !flint_eq(w, int_to_flint(1)))


PyDoc_STRVAR(rescale_docstring, "\
Rescale an array of 4-length homogenous coordinates x,y,z,w -> x/w,y/w,z/w,1");

/**
 * Type generic rescale function macro
 * 
 * :param TYPE: The c type (float, double, flint)
 * :param COMP: The comparison operations
 */
#define PYAFFINE_RESCALE(TYPE, COMP)\
static void pyaffine_rescale_##TYPE(char** args,\
                                  npy_intp const* dims,\
                                  npy_intp const* strides,\
                                  void* data) {\
    npy_intp i, n;\
    npy_intp N = dims[0];\
    char* h_in_base = args[0];\
    char* h_in;\
    char* h_out_base = args[1];\
    char* h_out;\
    npy_intp d_h_in_n = strides[0];\
    npy_intp d_h_out_n = strides[1];\
    npy_intp d_h_in_i = strides[2];\
    npy_intp d_h_out_i = strides[3];\
    TYPE w;\
    for (n=0; n<N; n++) {\
        w = *((TYPE*) (h_in_base + 3*d_h_in_i));\
        if (COMP) {\
            for( i=0; i<3; i++) {\
                h_in = h_in_base + i*d_h_in_i;\
                h_out = h_out_base + i*d_h_out_i;\
                *((TYPE*) h_out) = TYPE##_divide(*((TYPE*) h_in), w);\
            }\
            h_out = h_out_base + 3*d_h_out_i;\
            *((TYPE*) h_out) = int_to_##TYPE(1);\
        }\
        h_in_base += d_h_in_n;\
        h_out_base += d_h_out_n;\
    }\
}

PYAFFINE_RESCALE(float, fabs(w-((float) 1.0)) > (float) ALMOST_EQUAL_EPS)
PYAFFINE_RESCALE(double, abs(w - 1.0) > ALMOST_EQUAL_EPS)
PYAFFINE_RESCALE(flint, !flint_eq(w, int_to_flint(1)))

static PyMethodDef AffineMethods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_c_trans",
    .m_doc = "4x4 geometric transforms",
    .m_size = -1,
    .m_methods = AffineMethods,
};

PyUFuncGenericFunction rescale_loopfuncs[] = {
    &pyaffine_rescale_double,
    &pyaffine_rescale_float};
static const char rescale_builtin_types[] = {
    NPY_DOUBLE, NPY_DOUBLE, 
    NPY_FLOAT, NPY_FLOAT};

PyUFuncGenericFunction apply_loopfuncs[] = {
    &pyaffine_apply_vert_double,
    &pyaffine_apply_vert_float};
static const char apply_builtin_types[] = {
    NPY_DOUBLE, NPY_DOUBLE, NPY_DOUBLE, 
    NPY_FLOAT, NPY_FLOAT, NPY_FLOAT};

// The module initialization function
PyMODINIT_FUNC PyInit__c_trans(void) {
    PyObject* m;
    PyObject* d;
    PyObject* ufunc;
    m = PyModule_Create(&moduledef);
    if (m==NULL) {
        PyErr_Print();
        PyErr_SetString(PyExc_SystemError, "Could not create affine module.");
        return NULL;
    }
    // Import and initialize numpy
    import_array();
    if (PyErr_Occurred()) {
        PyErr_Print();
        PyErr_SetString(PyExc_SystemError, "Could not initialize NumPy.");
        return NULL;
    }
    // Import flint c API
    if (import_flint() < 0) {
        PyErr_Print();
        PyErr_SetString(PyExc_SystemError, "Count not load flint c API");
        return NULL;
    }
    // Import numpys ufunc api
    import_ufunc();
    if (PyErr_Occurred()) {
        PyErr_Print();
        PyErr_SetString(PyExc_SystemError, "Could not load NumPy ufunc c API.");
        return NULL;
    }
    // Register the rescale ufuncs
    ufunc = PyUFunc_FromFuncAndDataAndSignature(
        rescale_loopfuncs, NULL, rescale_builtin_types, 2, 1, 1, PyUFunc_None,
        "rescale", rescale_docstring, 0, "(4)->(4)");
    int rescale_custom_types[] = {NPY_FLINT, NPY_FLINT};
    PyUFunc_RegisterLoopForType(
        (PyUFuncObject*) ufunc, NPY_FLINT,
        &pyaffine_rescale_flint, rescale_custom_types, NULL);
    d = PyModule_GetDict(m);
    PyDict_SetItemString(d, "rescale", ufunc);
    Py_DECREF(ufunc);
    // Register the apply_vert ufuncs  
    ufunc = PyUFunc_FromFuncAndDataAndSignature(
        apply_loopfuncs, NULL, apply_builtin_types, 2, 2, 1, PyUFunc_None,
        "apply_vert", apply_vert_docstring, 0, "(4,4),(3)->(3)");
    int apply_custom_types[] = {NPY_FLINT, NPY_FLINT, NPY_FLINT};
    PyUFunc_RegisterLoopForType(
        (PyUFuncObject*) ufunc, NPY_FLINT,
        &pyaffine_apply_vert_flint, apply_custom_types, NULL);
    d = PyModule_GetDict(m);
    PyDict_SetItemString(d, "apply_vert", ufunc);
    Py_DECREF(ufunc);

    return m;
}