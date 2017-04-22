__all__ = ['BioCAnnotation']

from meta import _MetaId, _MetaInfons, _MetaText

class BioCAnnotation(_MetaId, _MetaInfons, _MetaText):

    def __init__(self, annotation=None):
        
        self.id = ''
        self.infons = dict()
        self.locations = list()
        self.text = ''

        if annotation is not None:
            self.id = annotation.id
            self.infons = annotation.infons
            self.locations = annotation.locations
            self.text = self.text

    def __str__(self):
        s = 'id: ' + self.id + '\n'
        s += str(self.infons) + '\n'
        s += 'locations: ' + str(self.locations) + '\n'
        s += 'text: ' + self.text + '\n'

        return s

    def clear_locations(self):
        self.locations = list()

    def add_location(self, location):
        self.locations.append(location)
