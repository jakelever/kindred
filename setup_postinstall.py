from setuptools import setup
from setuptools.command.install import install
import os

def readme():
	with open('README.rst') as f:
		return f.read()

def _post_install():
	print('POST INSTALL')


class new_install(install):
	#def __init__(self, *args, **kwargs):
	#	super(new_install, self).__init__(*args, **kwargs)
		#atexit.register(_post_install)

	#def run(self):
	def __init__(self, *args, **kwargs):
		#raise RuntimeError('Oh dear')
		#install.run(self)
		super(type(self), self).__init__(*args, **kwargs)
		#print('WOOT')



setup(name='kindred',
	version='0.1',
	description='A relation extraction toolkit for biomedical text mining',
	long_description=readme(),
	classifiers=[
		'Intended Audience :: Developers',
		'Intended Audience :: Education',
		'Intended Audience :: Information Technology',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Topic :: Scientific/Engineering',
		'Topic :: Scientific/Engineering :: Artificial Intelligence',
		'Topic :: Scientific/Engineering :: Human Machine Interfaces',
		'Topic :: Scientific/Engineering :: Information Analysis',
		'Topic :: Text Processing',
		'Topic :: Text Processing :: General',
		'Topic :: Text Processing :: Indexing',
		'Topic :: Text Processing :: Linguistic',
	],
	url='http://github.com/jakelever/kindred',
	author='Jake Lever',
	author_email='jake.lever@gmail.com',
	license='MIT',
	packages=['kindred'],
	install_requires=['nltk','scikit-learn','numpy','scipy'],
	include_package_data=True,
	zip_safe=False,
	test_suite='nose.collector',
	tests_require=['nose'],
	cmdclass={'install': new_install})

