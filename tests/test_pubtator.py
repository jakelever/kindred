
import kindred

def test_pubtator_pmid():
	corpus = kindred.pubtator.load(19894120)

	assert isinstance(corpus,kindred.Corpus)

	docCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])
	
	assert docCount == 2
	assert relationCount == 0
	assert entityCount > 0

def test_pubtator_pmids():
	corpus = kindred.pubtator.load([19894120,19894121])

	assert isinstance(corpus,kindred.Corpus)

	docCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])
	
	assert docCount == 4
	assert relationCount == 0
	assert entityCount > 0
	
if __name__ == '__main__':
	test_pubtator()
