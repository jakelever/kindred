
import kindred
import os
import tempfile
import pytest
import pytest_socket
import shutil

def test_loadBioNLP_listTasks():
	expectedTaskNames = set()
	with open(os.path.join(os.path.dirname(kindred.bionlpst.__file__),'bionlpst_files.txt'),'r') as f:
		for line in f:
			taskName = line.strip().split('\t')[0]
			expectedTaskNames.add(taskName)

	assert set(kindred.bionlpst.listTasks()) == expectedTaskNames

def test_loadBioNLP_fail():
	pytest_socket.disable_socket()
	with pytest.raises(RuntimeError) as excinfo:
		corpus = kindred.bionlpst.load('2016-BB3-event-train')
	pytest_socket.enable_socket()
	assert excinfo.value.args == ('A test tried to use socket.socket.',)

def test_loadBioNLP_BB3_event_train():
	corpus = kindred.bionlpst.load('2016-BB3-event-train')#,ignoreEntities=['Title','Paragraph'])

	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])

	assert fileCount == 61
	assert relationCount == 327
	assert entityCount == 1224
		

def test_loadBioNLP_BB3_event_dev():
	corpus = kindred.bionlpst.load('2016-BB3-event-dev')#,,ignoreEntities=['Title','Paragraph'])

	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])

	assert fileCount == 34
	assert relationCount == 223
	assert entityCount == 816

def test_loadBioNLP_BB3_event_test():
	corpus = kindred.bionlpst.load('2016-BB3-event-test')#,,ignoreEntities=['Title','Paragraph'])
	
	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])

	assert fileCount == 51
	assert relationCount == 0
	assert entityCount == 1246

def test_loadBioNLP_SeeDev_binary_train():
	corpus = kindred.bionlpst.load('2016-SeeDev-binary-train')
	
	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])

	assert fileCount == 39
	assert relationCount == 1628
	assert entityCount == 3259

def test_loadBioNLP_SeeDev_binary_dev():
	corpus = kindred.bionlpst.load('2016-SeeDev-binary-dev')

	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])

	assert fileCount == 19
	assert relationCount == 819
	assert entityCount == 1607

def test_loadBioNLP_SeeDev_binary_test():
	corpus = kindred.bionlpst.load('2016-SeeDev-binary-test')

	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])

	assert fileCount == 29
	assert relationCount == 0
	assert entityCount == 2216

def test_loadBioNLP_SeeDev_full_train():
	corpus = kindred.bionlpst.load('2016-SeeDev-full-train')

	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])

	assert fileCount == 39
	assert relationCount == 1158
	assert entityCount == 3259

def test_loadBioNLP_SeeDev_full_dev():
	corpus = kindred.bionlpst.load('2016-SeeDev-full-dev')

	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])

	assert fileCount == 19
	assert relationCount == 588
	assert entityCount == 1607

def test_loadBioNLP_SeeDev_full_test():
	corpus = kindred.bionlpst.load('2016-SeeDev-full-test')
	
	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])

	assert fileCount == 29
	assert relationCount == 0
	assert entityCount == 2216

def test_bionlp_BB3_classifier():
	trainCorpus = kindred.bionlpst.load('2016-BB3-event-train')
	devCorpus = kindred.bionlpst.load('2016-BB3-event-dev')

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.532

def test_bionlp_SeeDev_classifier():
	trainCorpus = kindred.bionlpst.load('2016-SeeDev-binary-train')
	devCorpus = kindred.bionlpst.load('2016-SeeDev-binary-dev')

	predictionCorpus = devCorpus.clone()
	predictionCorpus.removeRelations()

	classifier = kindred.RelationClassifier()
	classifier.train(trainCorpus)
	
	classifier.predict(predictionCorpus)
	
	f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
	assert round(f1score,3) == 0.349


if __name__ == '__main__':
	test_loadBioNLP_BB3_event_train()
