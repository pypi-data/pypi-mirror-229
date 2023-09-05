#include "dtypes.h"
#include "cd_list.h"


int
cd_l_set(catdict *cd, PyObject *key, PyObject *item)
{
    // support del operation
    if (item == NULL) {

        // failed
        if (PyDict_DelItem(cd->dict_list, key) < 0)
            return -1;

        if (PyDict_Size(cd->dict_list) == 0) {
            Py_DECREF(cd->dict_list);
            cd->dict_list = NULL;
        }

        return 0;
    }

    if (!PyList_CheckExact(item)) {
        PyErr_SetString(PyExc_TypeError, "Except 'list' object");
        return -1;
    }

    if (cd->dict_list == NULL) {
        cd->dict_list = PyDict_New();

        // Error handling.
        if (cd->dict_list == NULL) {
            DEFAULT_ERR;
            return -1;
        }
    }

    return PyDict_SetItem(cd->dict_list, key, item);
}
