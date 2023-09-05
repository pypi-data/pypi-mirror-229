#include "dtypes.h"
#include "cd_set.h"


int
cd_s_set(catdict *cd, PyObject *key, PyObject *item)
{
    // support del operation
    if (item == NULL) {

        // failed
        if (PyDict_DelItem(cd->dict_set, key) < 0)
            return -1;

        if (PyDict_Size(cd->dict_set) == 0) {
            Py_DECREF(cd->dict_set);
            cd->dict_set = NULL;
        }

        return 0;
    }

    if (!PySet_CheckExact(item)) {
        PyErr_SetString(PyExc_TypeError, "Except 'set' object");
        return -1;
    }

    if (cd->dict_set == NULL) {
        cd->dict_set = PyDict_New();

        // Error handling.
        if (cd->dict_set == NULL) {
            DEFAULT_ERR;
            return -1;
        }
    }

    return PyDict_SetItem(cd->dict_set, key, item);
}
