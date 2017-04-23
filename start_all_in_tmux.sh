#!/bin/bash

tmux new-window -n MLDriveWebVis "cd webvis/node_modules/jsmpeglive/server; node stream-server-websockets.js"
tmux split-window -v -p 80 -t MLDriveWebVis "mosquitto -c mosquitto.conf"
tmux split-window -h -t MLDriveWebVis "cd webvis; npm start"
tmux split-window -v -t MLDriveWebVis "sleep 3; ffmpeg -f v4l2 -framerate 30 -video_size 320x240 -i /dev/video0 -b:v 500000 -f mpeg1video http://127.0.0.1:8082/320/240/"
tmux split-window -v -t MLDriveWebVis.1 "sh test_telemetry.sh"
