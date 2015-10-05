#!/bin/sh
fuser -n tcp -k 9002
sh /apps/cosc481/devops/server/runBackend.sh
