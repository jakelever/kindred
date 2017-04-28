__all__ = ['BioCPassage']

import sys
if sys.version_info >= (3, 0):
	from .meta import _MetaAnnotations, _MetaOffset, _MetaText, _MetaRelations, _MetaInfons
	from .compat import _Py2Next
else:
	from meta import _MetaAnnotations, _MetaOffset, _MetaText, _MetaRelations, _MetaInfons
	from compat import _Py2Next
	
class BioCPassage(_MetaAnnotations, _MetaOffset, _MetaText,
                  _MetaRelations, _MetaInfons):

    def __init__(self, passage=None):
        
        self.offset = '-1'
        self.text = ''
        self.infons = dict()
        self.sentences = list()
        self.annotations = list()
        self.relations = list()

        if passage is not None:
            self.offset = passage.offset
            self.text = passage.text
            self.infons = passage.infons
            self.sentences = passage.sentences
            self.annotations = passage.annotations
            self.relations = passage.relations

    def size(self):
        return len(self.sentences)

    def has_sentences(self):
        if len(self.sentences) > 0:
            return True

    def add_sentence(self, sentence):
        self.sentences.append(sentence)

    def sentences_iterator(self):
        return self.sentences.iterator() # TBD

    def clear_sentences(self):
        self.relations = list()

    def remove_sentence(self, sentence): # int or obj
        if type(sentence) is int:
            self.sentences.remove(self.sentences[sentence])
        else:
            self.sentences.remove(sentence)
