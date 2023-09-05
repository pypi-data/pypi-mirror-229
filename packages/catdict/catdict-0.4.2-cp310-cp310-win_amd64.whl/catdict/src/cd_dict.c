#include "dtypes.h"
#include "cd_dict.h"


int
cd_d_set(catdict *cd, PyObject *key, PyObject *item)
{
    // support del operation
    if (item == NULL) {

        // failed
        if (PyDict_DelItem(cd->dict_dict, key) < 0)
            return -1;

        if (PyDict_Size(cd->dict_dict) == 0) {
            Py_DECREF(cd->dict_dict);
            cd->dict_dict = NULL;
        }

        return 0;
    }

    if (!PyDict_CheckExact(item)) {
        PyErr_SetString(PyExc_TypeError, "Except 'dict' object");
        return -1;
    }

    if (cd->dict_dict == NULL) {
        cd->dict_dict = PyDict_New();

        // Error handling.
        if (cd->dict_dict == NULL) {
            DEFAULT_ERR;
            return -1;
        }
    }

    return PyDict_SetItem(cd->dict_dict, key, item);
}
