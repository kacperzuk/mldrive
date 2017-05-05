# mldrive

How to start everything currently?

1. `cd webvis; npm install`
2. `./start_all_in_tmux.sh`

or manually:

1. `cd webvis; npm install`
2. `mosquitto -c mosquitto.conf`
3. `cd webvis; npm start`
5. `cd vision; python ./vision.py 1 640 360 127.0.0.1`
6. `sh test_telemetry.sh`
