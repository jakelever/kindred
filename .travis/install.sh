#!/bin/bash
set -eo pipefail

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then

	# Install some custom requirements on OS X
	brew update

	case "${TOXENV}" in
	py27)
		# Install some custom Python 3.2 requirements on OS X
		brew upgrade python;
		pip2 install --upgrade virtualenv
		virtualenv env2 -p python2
		PS1=${PS1:=} source env2/bin/activate
		;;
	py36)
		brew install python3;
		pip3 install --upgrade virtualenv
		virtualenv env3 -p python3
		PS1=${PS1:=} source env3/bin/activate
		;;
	esac
else
	# Install some custom requirements on Linux
	sudo apt-get update
fi

python --version

