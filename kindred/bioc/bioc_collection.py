__all__ = ['BioCCollection']

from meta import _MetaInfons, _MetaIter
from compat import _Py2Next

class BioCCollection(_Py2Next, _MetaInfons, _MetaIter):

    def __init__(self, collection=None):
        
        self.infons = dict()
        self.source = ''
        self.date = ''
        self.key = ''
        self.documents = list()

        if collection is not None:
            self.infons = collection.infons
            self.source = collection.source
            self.date = collection.date
            self.key = collection.key
            self.documents = collection.documents

    def __str__(self):
        s = 'source: ' + self.source + '\n'
        s += 'date: ' + self.date + '\n'
        s += 'key: ' + self.key + '\n'
        s += str(self.infons) + '\n'
        s += str(self.documents) + '\n'

        return s

    def _iterdata(self):
        return self.documents
       
    def clear_documents(self):
        self.documents = list()

    def get_document(self, doc_idx):
        return self.documents[doc_idx] 

    def add_document(self, document):
        self.documents.append(document)

    def remove_document(self, document):
       if type(document) is int:
           self.dcouments.remove(self.documents[document])
       else:
           self.documents.remove(document) # TBC
