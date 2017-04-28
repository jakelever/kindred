__all__ = []

__author__ = 'Hernani Marques (h2m@access.uzh.ch)'

import sys
if sys.version_info >= (3, 0):
	from ._bioc_meta import _MetaAnnotations, _MetaInfons, _MetaOffset, \
						   _MetaRelations, _MetaText, _MetaId
	from ._iter import _MetaIter
else:
	from _bioc_meta import _MetaAnnotations, _MetaInfons, _MetaOffset, \
						   _MetaRelations, _MetaText, _MetaId
	from _iter import _MetaIter
