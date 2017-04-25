
import kindred

def test_pubtator():
	data = kindred.pubtator.load([19894120,19894121])

	assert isinstance(data,list)
	for d in data:
		assert isinstance(d,kindred.RelationData)

	fileCount = len(data)
	entityCount = sum([ len(d.getEntities()) for d in data ])
	relationCount = sum([ len(d.getRelations()) for d in data ])
	
	assert fileCount == 2
	assert relationCount == 0
	assert entityCount == 17
	
if __name__ == '__main__':
	test_pubtator()
