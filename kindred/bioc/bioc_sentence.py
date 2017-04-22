__all__ = ['BioCSentence']


from meta import _MetaAnnotations, _MetaInfons, _MetaOffset, \
                      _MetaRelations, _MetaText
                      

class BioCSentence(_MetaAnnotations, _MetaInfons, _MetaOffset, 
                   _MetaRelations, _MetaText):
    
    def __init__(self, sentence=None):
        
        self.offset = '-1'
        self.text = ''
        self.infons = dict()
        self.annotations = list()
        self.relations = list()

        if sentence is not None:
            self.offset = sentence.offset
            self.text = sentence.text
            self.infons = sentence.infons
            self.annotations = sentence.annotations
            self.relations = sentence.relations

    def __str__(self):
        s = 'offset: ' + str(self.offset) + '\n'
        s += 'infons: ' + str(self.infons) + '\n' # TBD
        s += 'text: ' + str(self.text) + '\n' # TBD
        s += str(self.annotations) + '\n' # TBD
        s += str(self.relations) + '\n' # TBD

        return s
