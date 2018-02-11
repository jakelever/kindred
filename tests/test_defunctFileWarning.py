
import kindred
import shutil
import os
from six.moves import reload_module

def test_defunctFileWarning(capsys):
	defunctFileLocation = os.path.expanduser('~/.kindred')
	created = False
	if not os.path.isdir(defunctFileLocation):
		created = True
		os.makedirs(defunctFileLocation)

	reload_module(kindred)
	out, err = capsys.readouterr()
	assert out == ''
	assert err == 'WARNING: Defunct large files in ~/.kindred from older version. This directory can be safely removed.\n'

	if created:
		shutil.rmtree(defunctFileLocation)
