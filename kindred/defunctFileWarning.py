import kindred
import os
import sys

def checkForDefunctKindredFiles():
	"""
	Checks and warns about defunct files that can be deleted
	"""
	if os.path.isdir(os.path.expanduser('~/.kindred')):
		sys.stderr.write("WARNING: Defunct large files in ~/.kindred from older version. This directory can be safely removed.\n")
		sys.stderr.flush()

