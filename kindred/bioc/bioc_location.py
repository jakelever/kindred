__all__ = ['BioCLocation']

from meta import _MetaOffset

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
