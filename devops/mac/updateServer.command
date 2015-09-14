#!/bin/bash
if ! which greadlink > /dev/null; then
	echo “Installing dependancies… Mac is hard.”
	if ! which brew > /dev/null; then
		ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	fi
	brew install coreutils
fi
echo "Updating remote server -- pulling from github"
cd $(dirname $(greadlink -f $0))
ssh -i bin/identity.ppk 481_user@gat.im /apps/cosc481/devops/server/cloneGit.sh