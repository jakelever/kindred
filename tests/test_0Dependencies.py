import kindred
import kindred.Dependencies
import os
import shutil
import pytest

def test_corenlpFail():
		
	if os.path.isdir(kindred.Dependencies.downloadDirectory):
		shutil.rmtree(kindred.Dependencies.downloadDirectory)

	assert kindred.Dependencies.checkCoreNLPDownload() == False
	assert kindred.Dependencies.testCoreNLPConnection() == False

	with pytest.raises(RuntimeError) as excinfo:
		kindred.Dependencies.initializeCoreNLP()
	assert excinfo.value.args == ("Could not find the Stanford CoreNLP files. Use kindred.downloadCoreNLP() first",)

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
	if not kindred.Dependencies.testCoreNLPConnection():
		kindred.Dependencies.initializeCoreNLP()

	kindred.Dependencies.killCoreNLP()

	assert kindred.Dependencies.testCoreNLPConnection() == False

	kindred.Dependencies.initializeCoreNLP()

	assert kindred.Dependencies.testCoreNLPConnection() == True

if __name__ == '__main__':
	test_corenlpFail()
