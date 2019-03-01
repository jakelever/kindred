
import kindred
import os
import shutil
import tempfile
import hashlib

class TempDir:
	def __init__(self):
		pass

	def __enter__(self):
		self.tempDir = tempfile.mkdtemp()
		return self.tempDir

	def __exit__(self, type, value, traceback):
		shutil.rmtree(self.tempDir)

def test_loadBioNLP_findDir():
	with TempDir() as tempDir:
		actualDirPath = os.path.join(tempDir,'actualDir')
		os.mkdir(actualDirPath)
		assert kindred.utils._findDir('actualDir',tempDir) == actualDirPath
		assert kindred.utils._findDir('doesntExist',tempDir) == None

def test_corruptFileInWayOfDownload():
	with TempDir() as tempDir:
		fileInfo = ('https://github.com/jakelever/kindred/archive/1.0.tar.gz','1.0.tar.gz','363d36269a6ea83e1a253a0709dc365c3536ecd2976096ea0600cd4ef2f1e33c')

		expectedDownloadPath = os.path.join(tempDir,fileInfo[1])
		with open(expectedDownloadPath,'w') as f:
			f.write("\n".join(map(str,range(100))))

		oldSHA256 = hashlib.sha256(open(expectedDownloadPath, 'rb').read()).hexdigest()

		kindred.utils._downloadFiles([fileInfo],tempDir)

		newSHA256 = hashlib.sha256(open(expectedDownloadPath, 'rb').read()).hexdigest()

		assert oldSHA256 != newSHA256
		assert newSHA256 == fileInfo[2]


def test_downloadSubdir():
	with TempDir() as tempDir:
		downloadDir = os.path.join(tempDir,'toBeCreated')

		fileInfo = ('https://github.com/jakelever/kindred/archive/1.0.tar.gz','1.0.tar.gz','363d36269a6ea83e1a253a0709dc365c3536ecd2976096ea0600cd4ef2f1e33c')

		expectedDownloadPath = os.path.join(downloadDir,fileInfo[1])

		assert not os.path.isdir(downloadDir)
		kindred.utils._downloadFiles([fileInfo],downloadDir)
		assert os.path.isdir(downloadDir)

		newSHA256 = hashlib.sha256(open(expectedDownloadPath, 'rb').read()).hexdigest()

		assert newSHA256 == fileInfo[2]

