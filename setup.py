#!/usr/bin/env python

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

def readme():
	with open('README.rst') as f:
		return f.read()

setup(name='kindred',
	version='1.0.0',
	description='A relation extraction toolkit for biomedical text mining',
	long_description=long_description,
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
	install_requires=['scikit-learn','numpy','scipy','intervaltree','networkx','wget','pycorenlp','lxml','future','bioc','pytest_socket','six'],
	include_package_data=True,
	zip_safe=False,
	test_suite='nose.collector',
	tests_require=['nose'])

