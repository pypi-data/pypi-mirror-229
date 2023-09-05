#include "dtypes.h"
#include "cd_bool.h"


int
cd_b_set(catdict *cd, PyObject *key, PyObject *item)
{
    PyObject *o;

    // support del operation
    if (item == NULL) {

        // failed
        if (PyDict_DelItem(cd->dict_bool, key) < 0)
            return -1;

        if (PyDict_Size(cd->dict_bool) == 0) {
            Py_DECREF(cd->dict_bool);
            cd->dict_bool = NULL;
        }

        return 0;
    }

    if (PyBool_Check(item) || PyLong_CheckExact(item) || PyFloat_CheckExact(item)) {

        switch (PyObject_Not(item)) {
            case 0:
                o = Py_True;
                Py_INCREF(o);
                break;

            case 1:
                o = Py_False;
                Py_INCREF(o);
                break;

            default:
                DEFAULT_ERR;
                return -1;
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Except 'bool', 'int', or 'float' value.");
        return -1;
    };

    if (cd->dict_bool == NULL) {
        cd->dict_bool = PyDict_New();

        // Error handling.
        if (cd->dict_bool == NULL) {
            DEFAULT_ERR;
            return -1;
        }
    }

    return PyDict_SetItem(cd->dict_bool, key, o);
}
