
import kindred

def test_pubannotation():
	data = kindred.pubannotation.load('bionlp-st-gro-2013-development')

	assert isinstance(data,list)
	for d in data:
		assert isinstance(d,kindred.RelationData)

	fileCount = len(data)
	entityCount = sum([ len(d.getEntities()) for d in data ])
	relationCount = sum([ len(d.getRelations()) for d in data ])

	assert fileCount == 50
	assert relationCount == 1454
	assert entityCount == 2657
	
if __name__ == '__main__':
	test_pubannotation()
