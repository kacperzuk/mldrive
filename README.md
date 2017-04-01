# mldrive

How to start everything currently?

1. `mosquitto -c mosquitto.conf`
2. `cd webvis; npm install; npm start`
3. `while true; do mosquitto_pub -t device_beacon -m 1; mosquitto_pub -t 1/telemetry/voltage/battery -m 3300; sleep 1; done`
