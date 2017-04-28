__all__ = ['BioCLocation']

import sys
if sys.version_info >= (3, 0):
    from .meta import _MetaOffset
    from .compat import _Py2Next
else:
    from meta import _MetaOffset
    from compat import _Py2Next

class BioCLocation(_MetaOffset):

    def __init__(self, location=None):
        
        self.offset = '-1'
        self.length = '0'

        if location is not None:
             self.offset = location.offset
             self.length = location.length 

    def __str__(self):
        s = str(self.offset) + ':' + str(self.length)

        return s
