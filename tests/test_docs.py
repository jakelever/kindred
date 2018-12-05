import os
import subprocess

def test_docs():
	scriptDir = os.path.dirname(__file__)
	docDir = os.path.join(os.path.dirname(scriptDir),'docs')
	try:
		os.chdir(docDir)
		output = subprocess.check_output(['make', 'html'], stderr=subprocess.STDOUT)
	finally:
		os.chdir(scriptDir)

	if isinstance(output,bytes):
		output = output.decode("utf-8")

	hasWarningOrError = [ line for line in output.split('\n') if isinstance(line,str) and ("warning" in line.lower() or "error" in line.lower()) ]
	for line in hasWarningOrError:
		print(line)
	assert len(hasWarningOrError) == 0, "Found %d lines with a warning or error in document build" % (len(hasWarningOrError))

if __name__ == '__main__':
	test_docs()
