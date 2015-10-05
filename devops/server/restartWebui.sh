#!/bin/sh
fuser -n tcp -k 8080
/apps/cosc481/devops/server/runWebui.sh
