#!/usr/bin/env python

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

import sys
if sys.version_info[0] < 3:
	raise Exception("PubRunner requires Python 3")

VERSION='2.8.0'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
	requirements = f.readlines()

setup(name='kindred',
	version=VERSION,
	description='A relation extraction toolkit for biomedical text mining',
	long_description=long_description,
	long_description_content_type='text/markdown',
	classifiers=[
		'Intended Audience :: Developers',
		'Intended Audience :: Education',
		'Intended Audience :: Information Technology',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: MIT License',
		'Operating System :: Unix',
		'Operating System :: MacOS :: MacOS X',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
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
	install_requires=requirements,
	include_package_data=True,
	zip_safe=False,
	test_suite='nose.collector',
	tests_require=['nose'])

