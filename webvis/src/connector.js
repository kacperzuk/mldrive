import MQTT from 'mqtt';
import { newDevice, updateTelemetry } from './actions';

class Connector {
  constructor(store) {
    this.client = MQTT.connect("ws://localhost:9001");
    this.client.subscribe("/device_beacon");
    this.client.on("message", this.handleMessage.bind(this));
    this.send_intervals = {};
  }
  init(store) {
    this.store = store;
  }
  handleMessage(topic, payload) {
    const t = topic.split("/");
    if(t[1] === "device_beacon") {
      this.handleDeviceBeacon(t, payload);
    } else if (t[2] === "telemetry") {
      this.handleDeviceTelemetry(t, payload);
    } else {
      console.warn("Unhandled MQTT topic:", topic);
    }
  }
  handleDeviceBeacon(topic, payload) {
    this.client.subscribe(`/${payload}/telemetry/#`);
    if(this.store) {
      this.store.dispatch(newDevice(payload.toString()));
    }
  }
  handleDeviceTelemetry(topic, payload) {
    const device_id = topic[1];
    const telemetry = topic.slice(3).join("/");
    if(this.store) {
      this.store.dispatch(updateTelemetry(device_id, telemetry, payload.toString()));
    }
  }
  sendOnce(topic, payload, qos=2) {
    this.client.publish(topic, payload, { qos });
  }
  setSendInterval(topic, payload, interval) {
    this.clearSendInterval(topic);
    this.send_intervals.push(setInterval(() => {
      this.sendOnce(topic, payload, 0);
    }, interval));
  }
  clearSendInterval(topic) {
    if(!this.send_intervals[topic]) {
      return;
    }
    clearInterval(this.send_intervals[topic]);
    delete this.send_intervals[topic];
  }
}

const connector = new Connector();

export default connector;
