# mldrive

How to start everything currently?

1. `mosquitto -c mosquitto.conf`
2. `cd webvis; npm install; npm start`
3. `while true; do mosquitto_pub -t device_beacon -m 1; mosquitto_pub -t 1/telemetry/voltage/battery -m 3300; mosquitto_pub -t 1/telemetry/temperature/ambient -m 205; mosquitto_pub -t 1/telemetry/temperature/motor -m 105; mosquitto_pub -t 1/telemetry/temperature/esc -m 305; mosquitto_pub -t 1/telemetry/temperature/battery -m 405; sleep 1; done`
