# mldrive

How to start everything currently?

1. `cd webvis; npm install`
2. `./start_all_in_tmux.sh`

or manually:

1. `cd webvis; npm install`
2. `mosquitto -c mosquitto.conf`
3. `cd webvis; npm start`
4. `cd webvis/node_modules/jsmpeglive/server; node stream-server-websockets.js`
5. `ffmpeg -f v4l2 -framerate 30 -video_size 320x240 -i /dev/video0 -b:v 500000 -f mpeg1video http://127.0.0.1:8082/320/240/`
6. `sh test_telemetry.sh`
