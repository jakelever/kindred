
import kindred

def test_pubtator_pmid():
	corpus = kindred.pubtator.load(19894120)

	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])
	
	assert fileCount == 1
	assert relationCount == 0
	assert entityCount == 17

def test_pubtator_pmids():
	corpus = kindred.pubtator.load([19894120,19894121])

	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])
	
	assert fileCount == 2
	assert relationCount == 0
	assert entityCount == 38
	
if __name__ == '__main__':
	test_pubtator()
