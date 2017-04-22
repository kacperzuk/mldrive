while true; do
    mosquitto_pub -t device_beacon -m 1
    mosquitto_pub -t 1/camera_stream/0 -m http://127.0.0.1:8090/0.webm
    mosquitto_pub -t 1/telemetry/accelX -m 0.123
    mosquitto_pub -t 1/telemetry/accelY -m 0.123
    mosquitto_pub -t 1/telemetry/accelZ -m 9.7
    mosquitto_pub -t 1/telemetry/acceldX -m 0.123
    mosquitto_pub -t 1/telemetry/acceldY -m 0.123
    mosquitto_pub -t 1/telemetry/acceldZ -m 9.7
    mosquitto_pub -t 1/telemetry/speed -m 3
    mosquitto_pub -t 1/telemetry/enginePower -m 3
    mosquitto_pub -t 1/telemetry/steeringAngle -m 3
    mosquitto_pub -t 1/telemetry/voltage/battery -m 7.2
    mosquitto_pub -t 1/telemetry/voltage/cell1 -m 3.6
    mosquitto_pub -t 1/telemetry/voltage/cell2 -m 4.1
    mosquitto_pub -t 1/telemetry/voltage/3v3bus -m 3.4
    mosquitto_pub -t 1/telemetry/voltage/vcc -m 5.1
    mosquitto_pub -t 1/telemetry/temperature/ambient -m 20.7
    mosquitto_pub -t 1/telemetry/temperature/motor -m 10.3
    mosquitto_pub -t 1/telemetry/temperature/esc -m 30.1
    mosquitto_pub -t 1/telemetry/temperature/battery -m 40.5
    sleep 1
done
