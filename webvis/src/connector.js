import MQTT from 'mqtt';
import { newDevice, updateTelemetry } from './actions';

export default class Connector {
  constructor(store) {
    this.store = store;
    this.client = MQTT.connect("ws://localhost:9001");
    this.client.subscribe("device_beacon");
    this.client.on("message", this.handleMessage.bind(this));
  }
  handleMessage(topic, payload) {
    const t = topic.split("/");
    if(topic === "device_beacon") {
      this.handleDeviceBeacon(t, payload);
    } else if (t[1] === "telemetry") {
      this.handleDeviceTelemetry(t, payload);
    } else {
      console.warn("Unhandled MQTT topic:", topic);
    }
  }
  handleDeviceBeacon(topic, payload) {
    this.client.subscribe(`${payload}/telemetry/#`);
    this.store.dispatch(newDevice(payload.toString()));
  }
  handleDeviceTelemetry(topic, payload) {
    const device_id = topic[0];
    const telemetry = topic.slice(2).join("/");
    this.store.dispatch(updateTelemetry(device_id, telemetry, payload.toString()));
  }
}
