import sys
import types


IS_PY2 = sys.version_info[0] < 3
STR_TYPE = basestring if IS_PY2 else str
ITER_TYPES = (types.ListType, types.TupleType) if IS_PY2 else (list, tuple)
