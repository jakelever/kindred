__all__ = ['BioCRelation']

from compat import _Py2Next
from meta import _MetaId, _MetaInfons, _MetaIter
from bioc_node import BioCNode

class BioCRelation(_MetaId, _MetaInfons, _Py2Next, _MetaIter):

    def __init__(self, relation=None):
        
        self.id = ''
        self.nodes = list()
        self.infons = dict()

        if relation is not None:
            self.id = relation.id
            self.nodes = relation.nodes
            self.infons = relation.infons

    def __str__(self):
        s = 'id: ' + self.id + '\n'
        s += 'infons: ' + str(self.infons) + '\n'
        s += 'nodes: ' + str(self.nodes) + '\n'

        return s

    def _iterdata(self):
        return self.nodes

    def add_node(self, node, refid=None, role=None):
        # Discard arg ``node'' if optional args fully provided
        if (refid is not None) and (role is not None):
            self.add_node(refid=refid, role=role)
        else: # Only consider optional args if both set
            self.nodes.append(node)
