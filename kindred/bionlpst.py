"""
Importer for BioNLP Shared Task data
"""

import tempfile

import kindred


import zipfile
import hashlib
import os
import sys
import wget
import shutil
import six

if sys.version_info >= (3, 0):
	import urllib.request
else:
	import urllib

def _calcSHA256(filename):
	return hashlib.sha256(open(filename, 'rb').read()).hexdigest()

def _isDirEmpty(path):
	files = os.listdir(path)
	return files == []

def _findDir(name, path):
	assert os.path.isdir(path), "Must provide directory as path"
	for root, dirs, files in os.walk(path):
		if name in dirs:
			return os.path.abspath(os.path.join(root, name))
	return None

def _downloadFiles(files,downloadDirectory):
	assert _isDirEmpty(downloadDirectory)

	for url,shortName,expectedSHA256 in files:
		downloadedPath = os.path.join(downloadDirectory,shortName)

		if not os.path.isfile(downloadedPath):
			try:
				wget.download(url,out=downloadedPath,bar=None)
				
				downloadedSHA256 = _calcSHA256(downloadedPath)
				assert downloadedSHA256 == expectedSHA256, "SHA256 mismatch with downloaded file: %s" % shortName
				
				if shortName.endswith('.zip'):
					zip_ref = zipfile.ZipFile(downloadedPath, 'r')
					zip_ref.extractall(path=downloadDirectory)
					zip_ref.close()
			except:
				raise RuntimeError("Unable to download BioNLP ST files")


def load(taskName,ignoreEntities=[]):
	tempDir = tempfile.mkdtemp()

	taskOptions = {}

	# 2016-BB3-event-train
	files = [('http://2016.bionlp-st.org/tasks/bb2/BioNLP-ST-2016_BB-event_train.zip','BioNLP-ST-2016_BB-event_train.zip', '3b02adff92d8ba8814c9901f4af7681863569fe40cd0d87914258d48f989bb96')]
	expectedDir = 'BioNLP-ST-2016_BB-event_train'
	taskOptions['2016-BB3-event-train'] = (files,expectedDir,False)
	# 2016-BB3-event-dev
	files = [('http://2016.bionlp-st.org/tasks/bb2/BioNLP-ST-2016_BB-event_dev.zip','BioNLP-ST-2016_BB-event_dev.zip', '6d6555b425e42ecc4edf8ffc378439ba722c59922cdf6c5819959861ff683533')]
	expectedDir = 'BioNLP-ST-2016_BB-event_dev'
	taskOptions['2016-BB3-event-dev'] = (files,expectedDir,False)
	# 2016-BB3-event-test
	files = [('http://2016.bionlp-st.org/tasks/bb2/BioNLP-ST-2016_BB-event_test.zip','BioNLP-ST-2016_BB-event_test.zip', 'a1fce4657227bc55aaac5df72d2df615474e0d96a1518234d3e11b3af1e910e7')]
	expectedDir = 'BioNLP-ST-2016_BB-event_test'
	taskOptions['2016-BB3-event-test'] = (files,expectedDir,False)

	# 2016-SeeDev-binary-train
	files = [('http://2016.bionlp-st.org/tasks/seedev/BioNLP-ST-2016_SeeDev-binary_train.zip','BioNLP-ST-2016_SeeDev-binary_train.zip', 'ecca965ae09a31c5675cc2a62f238e0eb3a83c164a925a7e8984dd4d9dbcec84')]
	expectedDir = 'BioNLP-ST-2016_SeeDev-binary_train'
	taskOptions['2016-SeeDev-binary-train'] = (files,expectedDir,False)
	# 2016-SeeDev-binary-dev
	files = [('http://2016.bionlp-st.org/tasks/seedev/BioNLP-ST-2016_SeeDev-binary_dev.zip','BioNLP-ST-2016_SeeDev-binary_dev.zip', 'ea8e0f8bb1bc62982bb9a1a207df33a106c78b14aeb9a0701894943ec9262326')]
	expectedDir = 'BioNLP-ST-2016_SeeDev-binary_dev'
	taskOptions['2016-SeeDev-binary-dev'] = (files,expectedDir,False)
	# 2016-SeeDev-binary-test
	files = [('http://2016.bionlp-st.org/tasks/seedev/BioNLP-ST-2016_SeeDev-binary_test.zip','BioNLP-ST-2016_SeeDev-binary_test.zip', '744df7379a1777f7bdd92f37887f6ca03d15875bf8ae56389e409d5df9e614d2')]
	expectedDir = 'BioNLP-ST-2016_SeeDev-binary_test'
	taskOptions['2016-SeeDev-binary-test'] = (files,expectedDir,False)
	
	# 2016-SeeDev-full-train
	files = [('http://2016.bionlp-st.org/tasks/seedev/BioNLP-ST-2016_SeeDev-full_train.zip','BioNLP-ST-2016_SeeDev-full_train.zip', '52ac808251cf75a4c65f0227f53faf0d39dd6cb3a508becbce0a8dd131a2b7c4')]
	expectedDir = 'BioNLP-ST-2016_SeeDev-full_train'
	taskOptions['2016-SeeDev-full-train'] = (files,expectedDir,True)
	# 2016-SeeDev-full-dev
	files = [('http://2016.bionlp-st.org/tasks/seedev/BioNLP-ST-2016_SeeDev-full_dev.zip','BioNLP-ST-2016_SeeDev-full_dev.zip', '12a07592799197238a8b1b127b759e0d94dd30c52471538553006cafa2203638')]
	expectedDir = 'BioNLP-ST-2016_SeeDev-full_dev'
	taskOptions['2016-SeeDev-full-dev'] = (files,expectedDir,True)
	# 2016-SeeDev-full-test
	files = [('http://2016.bionlp-st.org/tasks/seedev/BioNLP-ST-2016_SeeDev-full_test.zip','BioNLP-ST-2016_SeeDev-full_test.zip', '253b45e1e0aae16f7ce19db4692633556d19fb9e5509e75dbb71de319fb7c2f5')]
	expectedDir = 'BioNLP-ST-2016_SeeDev-full_test'
	taskOptions['2016-SeeDev-full-test'] = (files,expectedDir,True)

	assert taskName in taskOptions.keys(), "%s not a valid option in %s" % (taskName, taskOptions.keys())
	filesToDownload,expectedDir,ignoreComplexRelations = taskOptions[taskName]

	try:
		_downloadFiles(filesToDownload,tempDir)
	except:
		exc_info = sys.exc_info()
		shutil.rmtree(tempDir)
		six.reraise(*exc_info)

	mainDir = _findDir(expectedDir,tempDir)

	corpus = kindred.loadDir(dataFormat='standoff',directory=mainDir,ignoreEntities=ignoreEntities,ignoreComplexRelations=ignoreComplexRelations)

	shutil.rmtree(tempDir)

	return corpus

