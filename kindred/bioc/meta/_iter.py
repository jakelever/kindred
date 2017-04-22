__all__ = []

class _MetaIter:

    def __iter__(self):
        return self._iterdata().__iter__()
