__all__ = ['BioCDocument']

from compat import _Py2Next
from meta import _MetaId, _MetaInfons, _MetaRelations, _MetaIter

class BioCDocument(_MetaId, _MetaInfons, _MetaRelations, _MetaIter,
                   _Py2Next):

    def __init__(self, document=None):

        self.id = ''
        self.infons = dict()
        self.relations = list()
        self.passages = list()

        if document is not None:
            self.id = document.id
            self.infons = document.infons
            self.relations = document.relations
            self.passages = document.passages

    def __str__(self):
        s = 'id: ' + self.id + '\n'
        s += 'infon: ' + str(self.infons) + '\n'
        s += str(self.passages) + '\n'
        s += 'relation: ' + str(self.relations) + '\n'

        return s

    def _iterdata(self):
        return self.passages

    def get_size(self):
        return self.passages.size() # As in Java BioC

    def clear_passages(self):
        self.passages = list()

    def add_passage(self, passage):
        self.passages.append(passage)

    def remove_passage(self, passage):
        if type(passage) is int:
            self.passages.remove(self.passages[passage])
        else:
            self.passages.remove(passage) # TBC
