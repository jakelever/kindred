__all__ = []

__author__ = 'Hernani Marques (h2m@access.uzh.ch)'

import sys
if sys.version_info >= (3, 0):
    from ._py2_next import _Py2Next
else:
    from _py2_next import _Py2Next
