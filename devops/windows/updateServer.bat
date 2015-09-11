echo Updating remote server -- pulling from github

%~dp0\bin\plink.exe -i %~dp0\bin\identity.ppk 481_user@gat.im /apps/cosc481/devops/server/cloneGit.sh
