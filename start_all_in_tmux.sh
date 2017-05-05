#!/bin/bash

tmux new-window -n MLDriveWebVis "cd webvis/node_modules/jsmpeglive/server; node stream-server-websockets.js"
tmux split-window -v -p 66 -t MLDriveWebVis "mosquitto -c mosquitto.conf"
tmux split-window -h -t MLDriveWebVis "cd webvis; npm start"
tmux split-window -v -t MLDriveWebVis "sleep 1; cd vision; ./vision2ws.sh 1 640 480 127.0.0.1"
tmux split-window -v -t MLDriveWebVis.1 "sh test_telemetry.sh"
tmux split-window -h -t MLDriveWebVis.0 "sleep 3; sh -c \"while true; do ffmpeg -f v4l2 -video_size 640x480 -i /dev/video0 -preset ultrafast -b:v 100000000 -tune zerolatency -c:v libx264 -f mpeg1video -framerate 60 'tcp://0.0.0.0:6000'; done\""
