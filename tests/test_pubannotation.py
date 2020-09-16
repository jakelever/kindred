
import kindred

def test_pubannotation():
	corpus = kindred.pubannotation.load('bionlp-st-gro-2013-development')

	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])

	assert fileCount == 50
	assert relationCount == 1454
	assert entityCount == 2657
	
if __name__ == '__main__':
	test_pubannotation()
