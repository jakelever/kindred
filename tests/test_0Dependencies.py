import kindred
import kindred.Dependencies
import os
import shutil
import pytest

def test_corenlpFail():
		
	if os.path.isdir(kindred.Dependencies.downloadDirectory):
		shutil.rmtree(kindred.Dependencies.downloadDirectory)

	with pytest.raises(RuntimeError) as excinfo:
		kindred.Dependencies.initializeCoreNLP()
	assert excinfo.value.args == ("Could not find the Stanford CoreNLP files. Use kindred.downloadCoreNLP() first",)

def test_corenlpDownload():
	if os.path.isdir(kindred.Dependencies.downloadDirectory):
		shutil.rmtree(kindred.Dependencies.downloadDirectory)
	
	kindred.Dependencies.downloadCoreNLP()

	kindred.Dependencies.initializeCoreNLP()

def test_corenlpDownloadTwice():
	kindred.Dependencies.downloadCoreNLP()

	kindred.Dependencies.downloadCoreNLP()

if __name__ == '__main__':
	test_corenlpFail()
