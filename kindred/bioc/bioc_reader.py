__all__ = ['BioCReader']

import StringIO

from lxml import etree

from bioc_annotation import BioCAnnotation
from bioc_collection import BioCCollection
from bioc_document import BioCDocument
from bioc_location import BioCLocation
from bioc_passage import BioCPassage
from bioc_sentence import BioCSentence
from bioc_node import BioCNode
from bioc_relation import BioCRelation

class BioCReader:
    """
    This class can be used to store BioC XML files in PyBioC objects, 
    for further manipulation.
    """

    def __init__(self, source, dtd_valid_file=None):
        """
        source:             File path to a BioC XML input document.
        dtd_valid_file:     File path to a BioC.dtd file. Using this
                            optional argument ensures DTD validation.
        """
        
        self.source = source
        self.collection = BioCCollection()
        self.xml_tree = etree.parse(source)
        
        if dtd_valid_file is not None:
            dtd = etree.DTD(dtd_valid_file)
            if dtd.validate(self.xml_tree) is False:
                raise(Exception(dtd.error_log.filter_from_errors()[0]))
                
    def read(self):
        """
        Invoke this method in order to read in the file provided by
        the source class variable. Only after this method has been
        called the BioCReader object gets populated.
        """
        self._read_collection()
            
    def _read_collection(self):
        collection_elem = self.xml_tree.xpath('/collection')[0]
        
        self.collection.source = collection_elem.xpath('source')[0].text
        self.collection.date = collection_elem.xpath('date')[0].text
        self.collection.key = collection_elem.xpath('key')[0].text
        
        infon_elem_list = collection_elem.xpath('infon')
        document_elem_list = collection_elem.xpath('document')
        
        self._read_infons(infon_elem_list, self.collection)
        self._read_documents(document_elem_list)
        
        
    def _read_infons(self, infon_elem_list, infons_parent_elem):
        for infon_elem in infon_elem_list:
            infons_parent_elem.put_infon(self._get_infon_key(infon_elem),
                                            infon_elem.text)

    def _read_documents(self, document_elem_list):
        for document_elem in document_elem_list:
            document = BioCDocument()
            document.id = document_elem.xpath('id')[0].text
            self._read_infons(document_elem.xpath('infon'), document)
            self._read_passages(document_elem.xpath('passage'),
                                document)
            self._read_relations(document_elem.xpath('relation'),
                                document)
            
            self.collection.add_document(document)

    def _read_passages(self, passage_elem_list, document_parent_elem):
        for passage_elem in passage_elem_list:
            passage = BioCPassage()
            self._read_infons(passage_elem.xpath('infon'), passage)
            passage.offset = passage_elem.xpath('offset')[0].text
            
            # Is this BioC document with <sentence>?
            if len(passage_elem.xpath('sentence')) > 0:
                self._read_sentences(passage_elem.xpath('sentence'),
                                    passage)
            else:
                # Is the (optional) text element available?
		try:
                    passage.text = passage_elem.xpath('text')[0].text
                except:
                    pass
                self._read_annotations(passage_elem.xpath('annotation'),
                                    passage)
                                    
            self._read_relations(passage_elem.xpath('relation'),
                                    passage)
            
            document_parent_elem.add_passage(passage)
    
    def _read_sentences(self, sentence_elem_list, passage_parent_elem):
        for sentence_elem in sentence_elem_list:
            sentence = BioCSentence()
            self._read_infons(sentence_elem.xpath('infon'), sentence)
            sentence.offset = sentence_elem.xpath('offset')[0].text
            sentence.text = sentence_elem.xpath('text')[0].text
            self._read_annotations(sentence_elem.xpath('annotation'),
                                    sentence)
            self._read_relations(sentence_elem.xpath('relation'),
                                    sentence)
            
            passage_parent_elem.add_sentence(sentence)
    
    def _read_annotations(self, annotation_elem_list, 
                            annotations_parent_elem):
        for annotation_elem in annotation_elem_list:
            annotation = BioCAnnotation()
            # Attribute id is just #IMPLIED, not #REQUIRED
            if 'id' in annotation_elem.attrib:
                annotation.id = annotation_elem.attrib['id']
            self._read_infons(annotation_elem.xpath('infon'),
                                annotation)
                                
            for location_elem in annotation_elem.xpath('location'):
                location = BioCLocation()
                location.offset = location_elem.attrib['offset']
                location.length = location_elem.attrib['length']
                
                annotation.add_location(location)
                
            annotation.text = annotation_elem.xpath('text')[0].text
            
            annotations_parent_elem.add_annotation(annotation)
        
    def _read_relations(self, relation_elem_list, relations_parent_elem):
        for relation_elem in relation_elem_list:
            relation = BioCRelation()
            # Attribute id is just #IMPLIED, not #REQUIRED
            if 'id' in relation_elem.attrib:
                relation.id = relation_elem.attrib['id']
            self._read_infons(relation_elem.xpath('infon'), relation)

            for node_elem in relation_elem.xpath('node'):
                node = BioCNode()
                node.refid = node_elem.attrib['refid']
                node.role = node_elem.attrib['role']
                
                relation.add_node(node)
            
            relations_parent_elem.add_relation(relation)
 
    def _get_infon_key(self, elem):
        return elem.attrib['key']
