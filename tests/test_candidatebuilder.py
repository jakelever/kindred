import kindred
from kindred.CandidateBuilder import CandidateBuilder

from kindred.datageneration import generateData,generateTestData
	
def test_simpleRelationCandidates():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer>. <drug id="3">Aspirin</drug> is the main cause of <disease id="4">boneitis</disease>. <relation type="treats" subj="1" obj="2" />'

	corpus = kindred.Corpus()
	doc = kindred.Document(text)
	corpus.addDocument(doc)
	
	candidateBuilder = CandidateBuilder()
	relTypes,candidateRelations,candidateClasses = candidateBuilder.build(corpus)
	
	assert relTypes == [('treats', 'obj', 'subj')]
	assert candidateClasses == [[0], [1], [0], [0]]
	assert len(candidateRelations) == 4
	
	sourceEntityIDsToEntityIDs = corpus.documents[0].getSourceEntityIDsToEntityIDs()

	assert candidateRelations[0].entityIDs == [sourceEntityIDsToEntityIDs['1'], sourceEntityIDsToEntityIDs['2']]
	assert candidateRelations[1].entityIDs == [sourceEntityIDsToEntityIDs['2'], sourceEntityIDsToEntityIDs['1']]
	assert candidateRelations[2].entityIDs == [sourceEntityIDsToEntityIDs['3'], sourceEntityIDsToEntityIDs['4']]
	assert candidateRelations[3].entityIDs == [sourceEntityIDsToEntityIDs['4'], sourceEntityIDsToEntityIDs['3']]

if __name__ == '__main__':
	test_simpleRelationCandidates()

