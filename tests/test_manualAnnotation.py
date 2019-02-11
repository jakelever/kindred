import kindred
import six

class FakeInput:
	def __init__(self,inputSeries):
		self.inputSeries = inputSeries

	def input(self,textToIgnore=None):
		assert len(self.inputSeries) > 0, "No more inputs to supply"
		nextOne = self.inputSeries[0]
		self.inputSeries = self.inputSeries[1:]
		return nextOne

def test_manuallyAnnotate(monkeypatch):
	text1 = "<drug>Erlotinib</drug> is an <gene>EGFR</gene> inhibitor. "
	text1 += "<gene>EGFR</gene> and <drug>Erlotinib</drug> are terms associated with lung cancer. "
	text1 += "The drug <drug>Gefitinib</drug> targets <gene>EGFR</gene>. "
	text2 = "<drug>Herceptin</drug> targets <gene>HER2</gene> receptor."

	corpus1 = kindred.Corpus(text1,loadFromSimpleTag=True)
	corpus2 = kindred.Corpus(text2,loadFromSimpleTag=True)

	corpus = kindred.Corpus()
	corpus.documents = corpus1.documents + corpus2.documents

	parser = kindred.Parser()
	parser.parse(corpus)

	candidateBuilder = kindred.CandidateBuilder(entityCount=2,acceptedEntityTypes=[('drug','gene')])
	candidateRelations = candidateBuilder.build(corpus)

	fakeInput = FakeInput(['inhibits','0','1','x'])
	monkeypatch.setattr('six.moves.input',fakeInput.input)
	annotatedCorpus,unannotatedCorpus = kindred.manuallyAnnotate(corpus,candidateRelations)

	assert len(annotatedCorpus.documents) == 1
	assert str(annotatedCorpus.documents[0]) == "<Document Erlotinib is an EGFR inhibitor. EGFR and Erlotinib are terms associated with lung cancer. The drug Gefitinib targets EGFR.  [<Entity drug:'Erlotinib' sourceid=1 [(0, 9)]>, <Entity gene:'EGFR' sourceid=2 [(16, 20)]>, <Entity gene:'EGFR' sourceid=3 [(32, 36)]>, <Entity drug:'Erlotinib' sourceid=4 [(41, 50)]>, <Entity drug:'Gefitinib' sourceid=5 [(99, 108)]>, <Entity gene:'EGFR' sourceid=6 [(117, 121)]>] [<Relation inhibits [<Entity drug:'Erlotinib' sourceid=1 [(0, 9)]>, <Entity gene:'EGFR' sourceid=2 [(16, 20)]>] None>, <Relation inhibits [<Entity drug:'Gefitinib' sourceid=5 [(99, 108)]>, <Entity gene:'EGFR' sourceid=6 [(117, 121)]>] None>]>"

	assert len(unannotatedCorpus.documents) == 1
	assert str(unannotatedCorpus.documents[0]) == "<Document Herceptin targets HER2 receptor. [<Entity drug:'Herceptin' sourceid=1 [(0, 9)]>, <Entity gene:'HER2' sourceid=2 [(18, 22)]>] []>"
