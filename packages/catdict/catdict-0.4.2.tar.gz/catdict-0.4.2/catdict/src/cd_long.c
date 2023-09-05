#include "dtypes.h"
#include "cd_long.h"


int
cd_i_set(catdict *cd, PyObject *key, PyObject *item)
{
    PyObject *o;

    // support del operation
    if (item == NULL) {

        // failed
        if (PyDict_DelItem(cd->dict_long, key) < 0)
            return -1;

        if (PyDict_Size(cd->dict_long) == 0) {
            Py_DECREF(cd->dict_long);
            cd->dict_long = NULL;
        }

        return 0;
    }

    if (PyBool_Check(item) || PyLong_CheckExact(item) || PyFloat_CheckExact(item)) {
        o = PyNumber_Long(item);

        if (o == NULL) {
            DEFAULT_ERR;
            return -1;
        };
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Except 'bool', 'int', or 'float' value.");
        return -1;
    };

    if (cd->dict_long == NULL) {
        cd->dict_long = PyDict_New();

        // Error handling.
        if (cd->dict_long == NULL) {
            DEFAULT_ERR;
            return -1;
        }
    }

    return PyDict_SetItem(cd->dict_long, key, o);
}
