#include "dtypes.h"
#include "cd_unicode.h"


int
cd_u_set(catdict *cd, PyObject *key, PyObject *item)
{
    // support del operation
    if (item == NULL) {

        // failed
        if (PyDict_DelItem(cd->dict_unicode, key) < 0)
            return -1;

        if (PyDict_Size(cd->dict_unicode) == 0) {
            Py_DECREF(cd->dict_unicode);
            cd->dict_unicode = NULL;
        }

        return 0;
    }

    if (!PyUnicode_CheckExact(item)) {
        PyErr_SetString(PyExc_TypeError, "Except 'str' object");
        return -1;
    }

    if (cd->dict_unicode == NULL) {
        cd->dict_unicode = PyDict_New();

        // Error handling.
        if (cd->dict_unicode == NULL) {
            DEFAULT_ERR;
            return -1;
        }
    }

    return PyDict_SetItem(cd->dict_unicode, key, item);
}
