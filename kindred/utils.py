
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
	if os.path.isdir(path):
		for root, dirs, files in os.walk(path):
			if name in dirs:
				return os.path.abspath(os.path.join(root, name))
	return None

def _downloadFiles(files,downloadDirectory):
	if not os.path.isdir(downloadDirectory):
		os.mkdir(downloadDirectory)

	for url,shortName,expectedSHA256 in files:
		downloadedPath = os.path.join(downloadDirectory,shortName)
		
		if os.path.isfile(downloadedPath):
			downloadedSHA256 = _calcSHA256(downloadedPath)
			if not downloadedSHA256 == expectedSHA256:
				os.remove(downloadedPath)

		if not os.path.isfile(downloadedPath):
			wget.download(url,out=downloadedPath,bar=None)
			
			downloadedSHA256 = _calcSHA256(downloadedPath)
			assert downloadedSHA256 == expectedSHA256, "SHA256 mismatch with downloaded file: %s" % shortName
			
			if shortName.endswith('.zip'):
				zip_ref = zipfile.ZipFile(downloadedPath, 'r')
				zip_ref.extractall(path=downloadDirectory)
				zip_ref.close()
	
