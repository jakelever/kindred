
import kindred
import os
import shutil
import tempfile

def test_loadBioNLP_findDir():
	tempDir = tempfile.mkdtemp()
	actualDirPath = os.path.join(tempDir,'actualDir')
	os.mkdir(actualDirPath)
	assert kindred.utils._findDir('actualDir',tempDir) == actualDirPath
	assert kindred.utils._findDir('doesntExist',tempDir) == None
	shutil.rmtree(tempDir)

