
import kindred

def test_pubannotation():
	corpus = kindred.pubannotation.load('bionlp-st-gro-2013-development')

	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])

	assert fileCount > 0
	assert relationCount > 0
	assert entityCount > 0
	
if __name__ == '__main__':
	test_pubannotation()
