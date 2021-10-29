import os
import tempfile
import hashlib
import tarfile
import json
import sys
import shutil
from subprocess import Popen, PIPE, STDOUT

class TempDir:
	def __init__(self):
		pass

	def __enter__(self):
		self.tempDir = tempfile.mkdtemp()
		return self.tempDir

	def __exit__(self, type, value, traceback):
		shutil.rmtree(self.tempDir)
		#pass

def test_tutorial_annotate():
	scriptDir = os.path.abspath(os.path.dirname(__file__))
	tutorialDir = os.path.join(os.path.dirname(scriptDir),'tutorial')

	with TempDir() as tmpDir:
		os.chdir(tmpDir)
		command = "python %s/annotate.py --corpus %s/corpus.txt --wordlists %s/city.txt,%s/country.txt --outDir annotations2" % (tutorialDir,tutorialDir,tutorialDir,tutorialDir)
		inputData = ['isCapital','0','1','0','1','0','0','1','1','0','0','x']

		if sys.version_info[0] < 3:
			p = Popen(command.split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT)
		else:
			p = Popen(command.split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT, encoding='utf8')

		stdout = p.communicate(input='\n'.join(inputData)+'\n')[0]
		print(stdout)

		tar = tarfile.open(os.path.join(tutorialDir,'annotations.tar.gz'), "r:gz")
		tar.extractall()
		tar.close()

		expectedHashes = {}
		for root, dirs, files in os.walk('annotations'):
			for f in files:
				fullname = os.path.join(root,f)
				fileHash = hashlib.sha256(open(fullname, 'rb').read()).hexdigest()
				withoutAnnotationsDir = "/".join(fullname.split("/")[1:])
				expectedHashes[withoutAnnotationsDir] = fileHash

		newHashes = {}
		for root, dirs, files in os.walk('annotations2'):
			for f in files:
				fullname = os.path.join(root,f)
				fileHash = hashlib.sha256(open(fullname, 'rb').read()).hexdigest()
				withoutAnnotationsDir = "/".join(fullname.split("/")[1:])
				newHashes[withoutAnnotationsDir] = fileHash

		print('expectedHashes',expectedHashes)
		print('newHashes',newHashes)
		assert expectedHashes == newHashes, "Output of the annotate example run doesn't match the contents of annotations.tar.gz!"

def test_tutorial_buildAndUseClassifier():
	scriptDir = os.path.abspath(os.path.dirname(__file__))
	tutorialDir = os.path.join(os.path.dirname(scriptDir),'tutorial')

	with TempDir() as tmpDir:
		os.chdir(tmpDir)

		tar = tarfile.open(os.path.join(tutorialDir,'annotations.tar.gz'), "r:gz")
		tar.extractall()
		tar.close()

		command = "python %s/buildAndUseClassifier.py --dataToBuildModel annotations/annotated_relations/ --dataToApplyModel annotations/missing_relations/ --outDir predicted_relations" % tutorialDir

		expectedOutputStart = """Loading corpora...
Building classifier...
Applying classifier...
Saving results to directory...

Predicted relations:
"""

		if sys.version_info[0] < 3:
			p = Popen(command.split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT)
		else:
			p = Popen(command.split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT, encoding='utf8')
		stdout = p.communicate(input='\n')[0]
		print(stdout)

		assert expectedOutputStart in stdout
		
		foundRelations = [ r for r in stdout[len(expectedOutputStart):].split('\n') if r ]
		assert len(foundRelations) >= 3
		
		expected_files = ['00000000.a1', '00000000.a2', '00000000.txt', '00000001.a1', '00000001.a2', '00000001.txt', '00000002.a1', '00000002.a2', '00000002.txt', '00000003.a1', '00000003.a2', '00000003.txt', '00000004.a1', '00000004.a2', '00000004.txt', '00000005.a1', '00000005.a2', '00000005.txt', '00000006.a1', '00000006.a2', '00000006.txt', '00000007.a1', '00000007.a2', '00000007.txt']
		found_files = sorted(os.listdir('predicted_relations'))

		print(found_files)
		assert expected_files == found_files

if __name__ == '__main__':
	test_tutorial_buildAndUseClassifier()

