#include <Python.h>
#include <mydist.h>

static PyObject *mdist(PyObject *self, PyObject *args) {
  double x{0.};
  double y{0.};
  double shift{0.};
  if (!PyArg_ParseTuple(args, "ddd", &x, &y, &shift)) {
    return NULL;
  }
  MyDist mdist(shift);

  return PyFloat_FromDouble(mdist.dist(x, y));
}

static PyMethodDef module_methods[] = {{"mdist", mdist, METH_VARARGS, "TODO"},
                                       {NULL, NULL, 0, NULL}};
static struct PyModuleDef moduledef = {PyModuleDef_HEAD_INIT, "MAZAlib", "", -1,
                                       module_methods};

PyMODINIT_FUNC PyInit_MAZAlib(void) {
  // Py_Initialize();

  PyObject *module = PyModule_Create(&moduledef);
  if (!module) {
    return NULL;
  }
  return module;
}