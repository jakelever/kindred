import kindred
import kindred.Dependencies
import os
import shutil
import pytest
import pytest_socket



def test_corenlpFail():
	if kindred.Dependencies.testCoreNLPConnection():
		kindred.Dependencies.killCoreNLP()
	if os.path.isdir(kindred.Dependencies.downloadDirectory):
		shutil.rmtree(kindred.Dependencies.downloadDirectory)

	assert kindred.Dependencies.checkCoreNLPDownload() == False
	assert kindred.Dependencies.testCoreNLPConnection() == False

	with pytest.raises(RuntimeError) as excinfo:
		kindred.Dependencies.initializeCoreNLP()
	assert excinfo.value.args == ("Unable to find local server so trying to initialize CoreNLP instance. Could not find the Stanford CoreNLP files. Use kindred.downloadCoreNLP() first if subprocess should be used.",)


def test_corenlpOld():
	if kindred.Dependencies.testCoreNLPConnection():
		kindred.Dependencies.killCoreNLP()
	if os.path.isdir(kindred.Dependencies.downloadDirectory):
		shutil.rmtree(kindred.Dependencies.downloadDirectory)

	fakeCoreNLPDirectory = os.path.join(kindred.Dependencies.downloadDirectory,'stanford-corenlp-full-1970-01-01')
	os.makedirs(fakeCoreNLPDirectory)
	assert os.path.isdir(fakeCoreNLPDirectory)

	assert kindred.Dependencies.hasOldCoreNLP() == True
	
	text = 'You need to turn in your homework by next week'
	corpus = kindred.Corpus(text)
	
	parser = kindred.Parser()

	with pytest.raises(RuntimeError) as excinfo:
		parser.parse(corpus)

	assert excinfo.value.args == ("Kindred needs a newer version of CoreNLP. Please use kindred.downloadCoreNLP() to upgrade to the latest version (and clear out the old version)",)

def test_parseFailWithNoCoreNLP():
	if kindred.Dependencies.testCoreNLPConnection():
		kindred.Dependencies.killCoreNLP()
	if os.path.isdir(kindred.Dependencies.downloadDirectory):
		shutil.rmtree(kindred.Dependencies.downloadDirectory)

	assert kindred.Dependencies.checkCoreNLPDownload() == False
	assert kindred.Dependencies.testCoreNLPConnection() == False
	
	text = 'You need to turn in your homework by next week'
	corpus = kindred.Corpus(text)
	
	parser = kindred.Parser()

	with pytest.raises(RuntimeError) as excinfo:
		parser.parse(corpus)
	assert excinfo.value.args == ("Unable to find local server so trying to initialize CoreNLP instance. Could not find the Stanford CoreNLP files. Use kindred.downloadCoreNLP() first if subprocess should be used.",)

def test_corenlpDownloadFail():
	if kindred.Dependencies.testCoreNLPConnection():
		kindred.Dependencies.killCoreNLP()
	if os.path.isdir(kindred.Dependencies.downloadDirectory):
		shutil.rmtree(kindred.Dependencies.downloadDirectory)
	
	assert kindred.Dependencies.checkCoreNLPDownload() == False
	assert kindred.Dependencies.testCoreNLPConnection() == False

	pytest_socket.disable_socket()
	with pytest.raises(RuntimeError) as excinfo:
		kindred.Dependencies.downloadCoreNLP()
	pytest_socket.enable_socket()
	assert excinfo.value.args == ("A test tried to use socket.socket.",)

def test_corenlpDownload():
	if kindred.Dependencies.testCoreNLPConnection():
		kindred.Dependencies.killCoreNLP()
	if os.path.isdir(kindred.Dependencies.downloadDirectory):
		shutil.rmtree(kindred.Dependencies.downloadDirectory)
	
	assert kindred.Dependencies.checkCoreNLPDownload() == False
	assert kindred.Dependencies.testCoreNLPConnection() == False
	
	# We'll make this trickier.
	fakeCoreNLPDirectory = os.path.join(kindred.Dependencies.downloadDirectory,'stanford-corenlp-full-1970-01-01')
	fakeCoreNLPArchive = os.path.join(kindred.Dependencies.downloadDirectory,'stanford-corenlp-full-1970-01-01.zip')
	os.makedirs(fakeCoreNLPDirectory)
	with open(fakeCoreNLPArchive,'w') as f:
		f.write("\n".join(map(str,range(100))))
	assert os.path.isfile(fakeCoreNLPArchive)
	assert os.path.isdir(fakeCoreNLPDirectory)

	assert kindred.Dependencies.hasOldCoreNLP() == True

	kindred.Dependencies.downloadCoreNLP()

	assert kindred.Dependencies.checkCoreNLPDownload() == True
	assert kindred.Dependencies.testCoreNLPConnection() == False

	kindred.Dependencies.initializeCoreNLP()
	assert kindred.Dependencies.testCoreNLPConnection() == True
	assert kindred.Dependencies.hasOldCoreNLP() == False
	
	assert not os.path.isfile(fakeCoreNLPArchive)
	assert not os.path.isdir(fakeCoreNLPDirectory)

def test_corenlpDownloadTwice():
	kindred.Dependencies.downloadCoreNLP()

	kindred.Dependencies.downloadCoreNLP()

	assert kindred.Dependencies.checkCoreNLPDownload() == True

def test_corenlpKill():
	if not kindred.Dependencies.checkCoreNLPDownload():
		kindred.Dependencies.downloadCoreNLP()
	if not kindred.Dependencies.testCoreNLPConnection():
		kindred.Dependencies.initializeCoreNLP()

	kindred.Dependencies.killCoreNLP()

	assert kindred.Dependencies.testCoreNLPConnection() == False

def test_corenlpInitializeFail():
	if not kindred.Dependencies.checkCoreNLPDownload():
		kindred.Dependencies.downloadCoreNLP()
	if kindred.Dependencies.testCoreNLPConnection():
		kindred.Dependencies.killCoreNLP()

	assert kindred.Dependencies.testCoreNLPConnection() == False

	pytest_socket.disable_socket()

	with pytest.raises(RuntimeError) as excinfo:
		kindred.Dependencies.initializeCoreNLP()

	pytest_socket.enable_socket()

	assert excinfo.value.args == ("Unable to connect to launched CoreNLP subprocess",)

	assert kindred.Dependencies.testCoreNLPConnection() == False

def test_parseSucceedWithUninitializeCoreNLP():
	if not kindred.Dependencies.checkCoreNLPDownload():
		kindred.Dependencies.downloadCoreNLP()
	if kindred.Dependencies.testCoreNLPConnection():
		kindred.Dependencies.killCoreNLP()

	text = 'You need to turn in your homework by next week'
	corpus = kindred.Corpus(text)
	
	parser = kindred.Parser()

	parser.parse(corpus)

	# And again
	kindred.Dependencies.killCoreNLP()
	
	text2 = 'You need to turn in your homework by next week'
	corpus2 = kindred.Corpus(text2)
	
	parser2 = kindred.Parser()

	parser2.parse(corpus2)

def test_initializeTwice():
	if not kindred.Dependencies.checkCoreNLPDownload():
		kindred.Dependencies.downloadCoreNLP()

	kindred.Dependencies.initializeCoreNLP()

	kindred.Dependencies.initializeCoreNLP()

	assert kindred.Dependencies.checkCoreNLPDownload() == True

