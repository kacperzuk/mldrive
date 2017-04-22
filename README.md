# mldrive

How to start everything currently?

1. `mosquitto -c mosquitto.conf`
2. `cd webvis; npm install; npm start`
3. `cd webvis/node_modules/jsmpeglive/server; node stream-server-websockets.js`
4. `ffmpeg -f v4l2 -framerate 30 -video_size 320x240 -i /dev/video0 -b:v 500000 -f mpeg1video http://127.0.0.1:8082/320/240/`
5. `sh test_telemetry.sh`
