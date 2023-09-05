#ifndef CATDICT
#define CATDICT
#include "dtypes.h"

PyObject *
cd_status(catdict *cd, PyObject *Py_UNUSED(ignored));

PyObject *
cd_to_dict(catdict *cd, PyObject *Py_UNUSED(ignored));

PyObject *
cd_switch_unicode(catdict *cd, void *closure);

PyObject *
cd_switch_bool(catdict *cd, void *closure);

PyObject *
cd_switch_long(catdict *cd, void *closure);

PyObject *
cd_switch_float(catdict *cd, void *closure);

PyObject *
cd_switch_list(catdict *cd, void *closure);

PyObject *
cd_switch_tuple(catdict *cd, void *closure);

PyObject *
cd_switch_dict(catdict *cd, void *closure);

PyObject *
cd_switch_set(catdict *cd, void *closure);

int
cd_ignore(catdict *self, PyObject *value, void *closure);

PyObject *
cd_subscript(catdict *cd, PyObject *key);

int
cd_ass_subscript(catdict *cd, PyObject *key, PyObject *item);

#endif /* CATDICT */
