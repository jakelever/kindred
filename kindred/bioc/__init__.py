#
# Package for interoperability in BioCreative work
#

__version__ = '1.02'

__all__ = [
    'BioCAnnotation', 'BioCCollection', 'BioCDocument',
    'BioCLocation', 'BioCNode', 'BioCPassage', 'BioCRelation',
    'BioCSentence', 'BioCReader', 'BioCWriter'
    ]

__author__ = 'Hernani Marques (h2m@access.uzh.ch)'

from bioc_annotation import BioCAnnotation
from bioc_collection import BioCCollection
from bioc_document import BioCDocument
from bioc_location import BioCLocation
from bioc_node import BioCNode
from bioc_passage import BioCPassage
from bioc_relation import BioCRelation
from bioc_sentence import BioCSentence
from bioc_reader import BioCReader
from bioc_writer import BioCWriter
