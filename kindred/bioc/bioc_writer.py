__all__ = ['BioCWriter']

from lxml.builder import E
from lxml.etree import tostring

class BioCWriter:
    
    def __init__(self, filename=None, collection=None):
        
        self.root_tree = None
                        
        self.collection = None
        self.doctype = '''<?xml version='1.0' encoding='UTF-8'?>'''
        self.doctype += '''<!DOCTYPE collection SYSTEM 'BioC.dtd'>'''
        self.filename = filename
        
        if collection is not None:
            self.collection = collection
        
        if filename is not None:
            self.filename = filename
        
    def __str__(self):
        """ A BioCWriter object can be printed as string.
        """
        self._check_for_data()
            
        self.build()
        s = tostring(self.root_tree, 
                    pretty_print=True, 
                    doctype=self.doctype)
                    
        return s
    
    def _check_for_data(self):
        if self.collection is None:
            raise(Exception('No data available.'))
    
    def write(self, filename=None):
        """ Use this method to write the data in the PyBioC objects
            to disk.
            
            filename:   Output file path (optional argument; filename
                        provided by __init__ used otherwise.)
        """
        if filename is not None:
            self.filename = filename
        
        if self.filename is None:
            raise(Exception('No output file path provided.'))
            
        f = open(self.filename, 'w')
        f.write(self.__str__())
        
    def build(self):
        self._build_collection()
        
    def _build_collection(self):
        self.root_tree = E('collection', 
                            E('source'), E('date'), E('key'))
        self.root_tree.xpath('source')[0].text = self.collection.source
        self.root_tree.xpath('date')[0].text = self.collection.date
        self.root_tree.xpath('key')[0].text = self.collection.key         
        collection_elem = self.root_tree.xpath('/collection')[0]
        # infon*
        self._build_infons(self.collection.infons, collection_elem)
        # document+
        self._build_documents(self.collection.documents, 
                                collection_elem)
        
    def _build_infons(self, infons_dict, infons_parent_elem):
        for infon_key, infon_val in infons_dict.items():
            infons_parent_elem.append(E('infon'))
            infon_elem = infons_parent_elem.xpath('infon')[-1]
            
            infon_elem.attrib['key'] = infon_key
            infon_elem.text = infon_val
            
    def _build_documents(self, documents_list, collection_parent_elem):
        for document in documents_list:
            collection_parent_elem.append(E('document', E('id')))
            document_elem = collection_parent_elem.xpath('document')[-1]
            # id
            id_elem = document_elem.xpath('id')[0]
            id_elem.text = document.id
            # infon*
            self._build_infons(document.infons, document_elem)
            # passage+
            self._build_passages(document.passages, document_elem)
            # relation*
            self._build_relations(document.relations, document_elem)
            
    def _build_passages(self, passages_list, document_parent_elem):
        for passage in passages_list:
            document_parent_elem.append(E('passage'))
            passage_elem = document_parent_elem.xpath('passage')[-1]
            # infon*
            self._build_infons(passage.infons, passage_elem)
            # offset
            passage_elem.append(E('offset'))
            passage_elem.xpath('offset')[0].text = passage.offset
            if passage.has_sentences():
                # sentence*
                self._build_sentences(passage.sentences, passage_elem)
            else:
                # text?, annotation*
                passage_elem.append(E('text'))
                passage_elem.xpath('text')[0].text = passage.text
                self._build_annotations(passage.annotations, 
                                        passage_elem)
            # relation*
            self._build_relations(passage.relations, passage_elem)
        
    def _build_relations(self, relations_list, relations_parent_elem):
        for relation in relations_list:
            relations_parent_elem.append(E('relation'))
            relation_elem = relations_parent_elem.xpath('relation')[-1]
            # infon*
            self._build_infons(relation.infons, relation_elem)
            # node*
            for node in relation.nodes:
                relation_elem.append(E('node'))
                node_elem = relation_elem.xpath('node')[-1]
                node_elem.attrib['refid'] = node.refid
                node_elem.attrib['role'] = node.role
            # id (just #IMPLIED)
            if len(relation.id) > 0:
                relation_elem.attrib['id'] = relation.id
        
    def _build_annotations(self, annotations_list, 
                            annotations_parent_elem):
        for annotation in annotations_list:
            annotations_parent_elem.append(E('annotation'))
            annotation_elem = \
                annotations_parent_elem.xpath('annotation')[-1]
            # infon*
            self._build_infons(annotation.infons, annotation_elem)
            # location*
            for location in annotation.locations:
                annotation_elem.append(E('location'))
                location_elem = annotation_elem.xpath('location')[-1]
                location_elem.attrib['offset'] = location.offset
                location_elem.attrib['length'] = location.length
            # text
            annotation_elem.append(E('text'))
            text_elem = annotation_elem.xpath('text')[0]
            text_elem.text = annotation.text
            # id (just #IMPLIED)
            if len(annotation.id) > 0:
                annotation_elem.attrib['id'] = annotation.id

    def _build_sentences(self, sentences_list, passage_parent_elem):
        for sentence in sentences_list:
            passage_parent_elem.append(E('sentence'))
            sentence_elem = passage_parent_elem.xpath('sentence')[-1]
            # infon*
            self._build_infons(sentence.infons, sentence_elem)
            # offset
            sentence_elem.append(E('offset'))
            offset_elem = sentence_elem.xpath('offset')[0]
            offset_elem.text = sentence.offset
            # text?
            if len(sentence.text) > 0:
                sentence_elem.append(E('text'))
                text_elem = sentence_elem.xpath('text')[0]
                text_elem.text = sentence.text
            # annotation*
            self._build_annotations(sentence.annotations, sentence_elem)
            # relation*
            self._build_relations(sentence.relations, sentence_elem)
