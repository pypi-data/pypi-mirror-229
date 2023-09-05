#include "dtypes.h"
#include "cd_tuple.h"


int
cd_t_set(catdict *cd, PyObject *key, PyObject *item)
{
    // support del operation
    if (item == NULL) {

        // failed
        if (PyDict_DelItem(cd->dict_tuple, key) < 0)
            return -1;

        if (PyDict_Size(cd->dict_tuple) == 0) {
            Py_DECREF(cd->dict_tuple);
            cd->dict_tuple = NULL;
        }

        return 0;
    }

    if (!PyTuple_CheckExact(item)) {
        PyErr_SetString(PyExc_TypeError, "Except 'tuple' object");
        return -1;
    }

    if (cd->dict_tuple == NULL) {
        cd->dict_tuple = PyDict_New();

        // Error handling.
        if (cd->dict_tuple == NULL) {
            DEFAULT_ERR;
            return -1;
        }
    }

    return PyDict_SetItem(cd->dict_tuple, key, item);
}
