import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer

from kindred.datageneration import generateData,generateTestData
	
def test_simpleVectorizer():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer>. <drug id="3">Aspirin</drug> is the main cause of <disease id="4">boneitis</disease> . <relation type="treats" subj="1" obj="2" />'

	corpus = kindred.Corpus(text)
	
	candidateBuilder = CandidateBuilder()
	relTypes,candidateRelations,candidateClasses = candidateBuilder.build(corpus)
	
	# We'll just get the vectors for the selectedTokenTypes
	vectorizer = Vectorizer()
	vectors = vectorizer.transform(corpus,candidateRelations)
	
	tuples = [(0, 2),(1, 0),(2, 2),(3, 1),(0, 3),(1, 5),(2, 4),(3, 5)]
	expectedRows = [ r for r,c in tuples ]
	expectedCols = [ c for r,c in tuples ]
	
	rows,cols = vectors.nonzero()
	assert expectedRows == rows.tolist()
	assert expectedCols == cols.tolist()
	
	vectorsCSR = vectors.tocsr()
	for r,c in tuples:
		assert vectorsCSR[r,c] == 1.0
