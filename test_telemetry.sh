while true; do
    mosquitto_pub -t device_beacon -m 1
    mosquitto_pub -t 1/telemetry/accelX -m 12.3
    mosquitto_pub -t 1/telemetry/accelY -m 12.3
    mosquitto_pub -t 1/telemetry/accelZ -m 970
    mosquitto_pub -t 1/telemetry/acceldX -m 0.123
    mosquitto_pub -t 1/telemetry/acceldY -m 0.123
    mosquitto_pub -t 1/telemetry/acceldZ -m 9.7
    mosquitto_pub -t 1/telemetry/speed -m 3
    mosquitto_pub -t 1/telemetry/enginePower -m 3
    mosquitto_pub -t 1/telemetry/steeringAngle -m 90
    mosquitto_pub -t 1/telemetry/voltage/battery -m 7200
    mosquitto_pub -t 1/telemetry/voltage/cell1 -m 3100
    mosquitto_pub -t 1/telemetry/voltage/cell2 -m 4100
    mosquitto_pub -t 1/telemetry/voltage/3v3bus -m 3400
    mosquitto_pub -t 1/telemetry/voltage/vcc -m 5100
    mosquitto_pub -t 1/telemetry/temperature/ambient -m 200.7
    mosquitto_pub -t 1/telemetry/temperature/engine -m 100.3

    mosquitto_pub -t device_beacon -m 2
    mosquitto_pub -t 2/telemetry/accelX -m 2.3
    mosquitto_pub -t 2/telemetry/accelY -m 2.3
    mosquitto_pub -t 2/telemetry/accelZ -m 70
    mosquitto_pub -t 2/telemetry/acceldX -m 0.23
    mosquitto_pub -t 2/telemetry/acceldY -m 0.23
    mosquitto_pub -t 2/telemetry/acceldZ -m 19.7
    mosquitto_pub -t 2/telemetry/speed -m 3
    mosquitto_pub -t 2/telemetry/enginePower -m 30
    mosquitto_pub -t 2/telemetry/steeringAngle -m 50
    mosquitto_pub -t 2/telemetry/voltage/battery -m 200
    mosquitto_pub -t 2/telemetry/voltage/cell1 -m 100
    mosquitto_pub -t 2/telemetry/voltage/cell2 -m 100
    mosquitto_pub -t 2/telemetry/voltage/3v3bus -m 400
    mosquitto_pub -t 2/telemetry/voltage/vcc -m 100
    mosquitto_pub -t 2/telemetry/temperature/ambient -m 20.7
    mosquitto_pub -t 2/telemetry/temperature/engine -m 10.3
    sleep 1
done
