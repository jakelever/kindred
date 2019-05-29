import os
import tempfile
import hashlib
import tarfile
import json
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

		expectedOutput = """Loading corpora...
Building classifier...
Applying classifier...
Saving results to directory...

Predicted relations:
Delhi\tIndia
Nairobi\tKenya
"""

		p = Popen(command.split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT, encoding='utf8')
		stdout = p.communicate(input='\n')[0]
		print(stdout)

		assert stdout == expectedOutput

		expectedHashes = {'predicted_relations/00000002.txt': '9c4e0571dbcbf6e4771faf3cd52b342c66e12b71d660108b7d4ed44616f550a9', 'predicted_relations/00000001.a2': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'predicted_relations/00000000.txt': 'de088db44b953af6e620499bf775048b62bd34d4c1b0612eefe2d6b24daa11dc', 'predicted_relations/00000005.a1': '468bf51543ff111d27de0ad5114d4b97486cd723336808f7406b445f65b96bef', 'predicted_relations/00000006.a1': '8cdd9a3e8b0c7b891d61a1eb64c1f2a2ed2c7fbc51648b955408ebc1b838cb78', 'predicted_relations/00000007.txt': 'f0a33420449bf1191a296762ec20d9eacb381f9ca75674ea3f33ea4b27ed6e57', 'predicted_relations/00000007.a1': '656b537a249c4cc5b84259ebfa2f744b03385fe57f381ff609bf778452f2562b', 'predicted_relations/00000007.a2': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'predicted_relations/00000004.a2': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'predicted_relations/00000002.a2': '19fb550aa5184e6a2a755d77e91f7e29153a189503bc3abd8a793ecc67fcf715', 'predicted_relations/00000000.a2': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'predicted_relations/00000000.a1': '32d0592b3190507d0969271a3448cd6f3d169364852c2be6dd80ea0613288bd3', 'predicted_relations/00000001.a1': '591ba8124c0b04217fcc7472aa8507bceb85d0bfbfa3f747734ad7e73e5d71f7', 'predicted_relations/00000005.txt': 'ec35e551c0c148c1747a8b4d94c191533f5d9185eb47470a6bfd627455e998ee', 'predicted_relations/00000004.txt': '0d250812387e6cc295790fd7c21fab9fa17e2bbbfdb53473f2465b6892510050', 'predicted_relations/00000003.txt': '876d37fe2d7531f964e03bc761a887c769c61677fc311d196d603584d88c133d', 'predicted_relations/00000006.txt': '282b68a16f4405069c963f2236f3cd0c4cb82c219899889aa00003193bc3d4ee', 'predicted_relations/00000003.a2': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'predicted_relations/00000003.a1': 'de384edccf240c2557899320d20a32deb88ed7f00033850a260ecb8d2ceca258', 'predicted_relations/00000005.a2': '6891981f93d4fe333dbc969a2eb0890a080a3bc7b7a3c4dda453b40346762f7e', 'predicted_relations/00000002.a1': '00314718006a7def57d02f9d9efa97b79b6705813c80e5feb8644d31e9ffe32a', 'predicted_relations/00000004.a1': '00e4d1031b3682f21c9dd429e6044d9a081a913954499e55064864aec0f66238', 'predicted_relations/00000001.txt': '41f17059d8389c4d035d22d7ea323b7f38f46829aaa85c81b18c83a7c2bed669', 'predicted_relations/00000006.a2': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}

		newHashes = {}
		for root, dirs, files in os.walk('predicted_relations'):
			for f in files:
				fullname = os.path.join(root,f)
				fileHash = hashlib.sha256(open(fullname, 'rb').read()).hexdigest()
				newHashes[fullname] = fileHash

		assert expectedHashes == newHashes

if __name__ == '__main__':
	test_tutorial_buildAndUseClassifier()

