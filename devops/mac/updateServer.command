#!/bin/bash
echo "Updating remote server -- pulling from github"
cd $(dirname $(greadlink -f $0))
ssh -i bin/identity.ppk 481_user@gat.im /apps/cosc481/devops/server/cloneGit.sh