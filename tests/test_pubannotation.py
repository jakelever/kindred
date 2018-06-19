
import kindred

def test_pubannotation_groST():
	corpus = kindred.pubannotation.load('bionlp-st-gro-2013-development')

	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])

	assert fileCount == 50
	assert relationCount == 1454
	assert entityCount == 2657
	
def test_pubannotation_wikiPain():
	corpus = kindred.pubannotation.load('WikiPainGoldStandard')

	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])

	assert fileCount == 49
	assert relationCount == 299
	assert entityCount == 367

if __name__ == '__main__':
	test_pubannotation()
