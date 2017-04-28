import kindred
from kindred.bioc import *

if __name__ == '__main__':
	
	annotation1 = BioCAnnotation()
	annotation1.id = 'T1'
	annotation1.text = 'colorectal cancer'
	annotation1.locations = [BioCLocation()]
	annotation1.locations[0].offset = str(4)
	annotation1.locations[0].length = str(21-4)
	annotation1.infons['type'] = 'cancer'
	
	annotation2 = BioCAnnotation()
	annotation2.id = 'T2'
	annotation2.text = 'APC'
	annotation2.locations = [BioCLocation()]
	annotation2.locations[0].offset = str(49)
	annotation2.locations[0].length = str(52-49)
	annotation2.infons['type'] = 'gene'
	
	relation = BioCRelation()
	relation.id = 'R1'
	relation.nodes = [BioCNode(),BioCNode()]
	relation.nodes[0].refid = 'T1'
	relation.nodes[0].role = 'Cancer'
	relation.nodes[1].refid = 'T2'
	relation.nodes[1].role = 'Gene'
	relation.infons['type'] = 'causes'
	
	passage = BioCPassage()
	passage.text = 'The colorectal cancer was caused by mutations in APC'
	passage.annotations = [annotation1,annotation2]
	passage.relations = [relation]
	passage.offset = '0'
	

	document = BioCDocument()
	document.add_passage(passage)
	
	collection = BioCCollection()
	collection.add_document(document)
		
	writer = BioCWriter('out.bioc', collection)
	writer.write()
	
	print("Done")
	
