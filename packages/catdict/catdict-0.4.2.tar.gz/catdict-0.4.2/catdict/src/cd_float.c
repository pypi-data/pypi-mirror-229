#include "dtypes.h"
#include "cd_float.h"


int
cd_f_set(catdict *cd, PyObject *key, PyObject *item)
{
    PyObject *o;

    // support del operation
    if (item == NULL) {

        // failed
        if (PyDict_DelItem(cd->dict_float, key) < 0)
            return -1;

        if (PyDict_Size(cd->dict_float) == 0) {
            Py_DECREF(cd->dict_float);
            cd->dict_float = NULL;
        }

        return 0;
    }

    if (PyBool_Check(item) || PyLong_CheckExact(item) || PyFloat_CheckExact(item)) {
        o = PyNumber_Float(item);

        if (o == NULL) {
            DEFAULT_ERR;
            return -1;
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Except 'bool', 'int', or 'float' value.");
        return -1;
    };

    if (cd->dict_float == NULL) {
        cd->dict_float = PyDict_New();

        // Error handling.
        if (cd->dict_float == NULL) {
            DEFAULT_ERR;
            return -1;
        }
    }

    return PyDict_SetItem(cd->dict_float, key, o);
}
