import kindred
from kindred.CandidateBuilder import CandidateBuilder

from kindred.datageneration import generateData,generateTestData
	
def test_simpleRelationCandidates():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer>. <drug id="3">Aspirin</drug> is the main cause of <disease id="4">boneitis</disease>. <relation type="treats" subj="1" obj="2" />'

	data = [kindred.RelationData(text)]	
	
	candidateBuilder = CandidateBuilder()
	relTypes,candidateRelations,candidateClasses = candidateBuilder.build(data)
	
	assert relTypes == [('treats', 2)]
	assert candidateClasses == [[1], [0], [0], [0]]
	assert len(candidateRelations) == 4
	
	assert str(candidateRelations[0].processedSentence) == 'Erlotinib is a common treatment for NSCLC .'
	assert str(candidateRelations[1].processedSentence) == 'Erlotinib is a common treatment for NSCLC .'
	assert str(candidateRelations[2].processedSentence) == 'Aspirin is the main cause of boneitis .'
	assert str(candidateRelations[3].processedSentence) == 'Aspirin is the main cause of boneitis .'
	
	sourceEntityIDsToEntityIDs = data[0].getSourceEntityIDsToEntityIDs()

	assert candidateRelations[0].entitiesInRelation == (sourceEntityIDsToEntityIDs['1'], sourceEntityIDsToEntityIDs['2'])
	assert candidateRelations[1].entitiesInRelation == (sourceEntityIDsToEntityIDs['2'], sourceEntityIDsToEntityIDs['1'])
	assert candidateRelations[2].entitiesInRelation == (sourceEntityIDsToEntityIDs['3'], sourceEntityIDsToEntityIDs['4'])
	assert candidateRelations[3].entitiesInRelation == (sourceEntityIDsToEntityIDs['4'], sourceEntityIDsToEntityIDs['3'])

if __name__ == '__main__':
	test_simpleRelationCandidates()

