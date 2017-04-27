from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()

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
	install_requires=['nltk','scikit-learn','numpy','scipy','intervaltree','networkx','wget','pycorenlp','lxml'],
	include_package_data=True,
	zip_safe=False,
	test_suite='nose.collector',
	tests_require=['nose'])

