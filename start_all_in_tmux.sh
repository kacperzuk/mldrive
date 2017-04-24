#!/bin/bash

tmux new-window -n MLDriveWebVis "cd webvis/node_modules/jsmpeglive/server; node stream-server-websockets.js"
tmux split-window -v -p 80 -t MLDriveWebVis "mosquitto -c mosquitto.conf"
tmux split-window -h -t MLDriveWebVis "cd webvis; npm start"
tmux split-window -v -t MLDriveWebVis "sleep 3; cd vision; ./vision2ws.sh 1 640 360"
tmux split-window -v -t MLDriveWebVis.1 "sh test_telemetry.sh"
