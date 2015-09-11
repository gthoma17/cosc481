#!/bin/bash
cd /apps
rm -r cosc481
git clone git@github.com:gthoma17/cosc481.git
sh /apps/cosc481/devops/server/runBackend.sh
sh /apps/cosc481/devops/server/runWebui.sh
chmod -R 777 /apps/cosc481