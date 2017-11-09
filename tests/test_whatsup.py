import kindred
import kindred.Dependencies
import os
import shutil
import pytest
import pytest_socket


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


def test_corenlpKill():
	if not kindred.Dependencies.checkCoreNLPDownload():
		kindred.Dependencies.downloadCoreNLP()
	if not kindred.Dependencies.testCoreNLPConnection():
		kindred.Dependencies.initializeCoreNLP()

	assert kindred.Dependencies.testCoreNLPConnection() == True

	kindred.Dependencies.killCoreNLP()

	assert kindred.Dependencies.testCoreNLPConnection() == False

if __name__ == '__main__':
	test_parseFailWithNoCoreNLP()
	test_corenlpKill()

