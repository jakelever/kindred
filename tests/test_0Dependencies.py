import kindred
import kindred.Dependencies
import os
import shutil
import pytest
import pytest_socket

def test_corenlpFail():
	if os.path.isdir(kindred.Dependencies.downloadDirectory):
		shutil.rmtree(kindred.Dependencies.downloadDirectory)

	assert kindred.Dependencies.checkCoreNLPDownload() == False
	assert kindred.Dependencies.testCoreNLPConnection() == False

	with pytest.raises(RuntimeError) as excinfo:
		kindred.Dependencies.initializeCoreNLP()
	assert excinfo.value.args == ("Could not find the Stanford CoreNLP files. Use kindred.downloadCoreNLP() first",)

def test_parseFailWithNoCoreNLP():
	if os.path.isdir(kindred.Dependencies.downloadDirectory):
		shutil.rmtree(kindred.Dependencies.downloadDirectory)

	assert kindred.Dependencies.checkCoreNLPDownload() == False
	assert kindred.Dependencies.testCoreNLPConnection() == False
	
	text = 'You need to turn in your homework by next week'
	corpus = kindred.Corpus(text)
	
	parser = kindred.Parser()

	with pytest.raises(RuntimeError) as excinfo:
		parser.parse(corpus)
	assert excinfo.value.args == ("Cannot access local CoreNLP at http://localhost:9000 and cannot find CoreNLP files to launch subprocess. Please download using kindred.downloadCoreNLP() if subprocess should be used",)

def test_corenlpDownloadFail():
	if os.path.isdir(kindred.Dependencies.downloadDirectory):
		shutil.rmtree(kindred.Dependencies.downloadDirectory)
	
	assert kindred.Dependencies.checkCoreNLPDownload() == False
	assert kindred.Dependencies.testCoreNLPConnection() == False

	pytest_socket.disable_socket()
	with pytest.raises(RuntimeError) as excinfo:
		kindred.Dependencies.downloadCoreNLP()
	pytest_socket.enable_socket()
	assert excinfo.value.args == ("A test tried to use socket.socket.",)

def test_corenlpDownloadFail_corruptExistingFile():
	if os.path.isdir(kindred.Dependencies.downloadDirectory):
		shutil.rmtree(kindred.Dependencies.downloadDirectory)

	# Create a corrupt file that will fail a SHA256 test
	corenlpDownloadPath = os.path.join(kindred.Dependencies.downloadDirectory,'stanford-corenlp-full-2016-10-31.zip')
	os.mkdir(kindred.Dependencies.downloadDirectory)
	with open(corenlpDownloadPath,'w') as f:
		f.write("\n".join(map(str,range(100))))
	
	assert kindred.Dependencies.checkCoreNLPDownload() == False
	assert kindred.Dependencies.testCoreNLPConnection() == False

	pytest_socket.disable_socket()
	with pytest.raises(RuntimeError) as excinfo:
		kindred.Dependencies.downloadCoreNLP()
	pytest_socket.enable_socket()
	assert excinfo.value.args == ("A test tried to use socket.socket.",)

def test_corenlpDownload():
	if os.path.isdir(kindred.Dependencies.downloadDirectory):
		shutil.rmtree(kindred.Dependencies.downloadDirectory)
	
	assert kindred.Dependencies.checkCoreNLPDownload() == False
	assert kindred.Dependencies.testCoreNLPConnection() == False

	kindred.Dependencies.downloadCoreNLP()

	assert kindred.Dependencies.checkCoreNLPDownload() == True
	assert kindred.Dependencies.testCoreNLPConnection() == False

	kindred.Dependencies.initializeCoreNLP()
	assert kindred.Dependencies.testCoreNLPConnection() == True

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

	kindred.Dependencies.initializeCoreNLP()

	assert kindred.Dependencies.testCoreNLPConnection() == True

def test_initializeTwice():
	if not kindred.Dependencies.checkCoreNLPDownload():
		kindred.Dependencies.downloadCoreNLP()

	kindred.Dependencies.initializeCoreNLP()

	kindred.Dependencies.initializeCoreNLP()

	assert kindred.Dependencies.checkCoreNLPDownload() == True

def test_parseSucceedWithUninitializeCoreNLP():
	if not kindred.Dependencies.checkCoreNLPDownload():
		kindred.Dependencies.downloadCoreNLP()
	if kindred.Dependencies.testCoreNLPConnection():
		kindred.Dependencies.killCoreNLP()

	text = 'You need to turn in your homework by next week'
	corpus = kindred.Corpus(text)
	
	parser = kindred.Parser()

	parser.parse(corpus)
	

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

	kindred.Dependencies.initializeCoreNLP()

	assert kindred.Dependencies.testCoreNLPConnection() == True

if __name__ == '__main__':
	test_corenlpFail()
