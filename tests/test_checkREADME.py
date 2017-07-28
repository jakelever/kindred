
import os

def _README():
	thisDir = os.path.dirname(os.path.realpath(__file__))
	parentDir = os.path.dirname(thisDir)
	readmePath = os.path.join(parentDir,'README.rst')

	readmeTestPath = os.path.join(thisDir,'README.py')

	with open(readmePath) as readmeF,open(readmeTestPath,'w') as testF:
		for line in readmeF:
			if line.startswith('>>> '):
				testF.write(line[4:])

	import README
	
