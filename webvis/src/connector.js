import MQTT from 'mqtt';
import { newDevice, updateTelemetry } from './actions';

class Connector {
  constructor() {
    var c = location.hash.substr(1) || "127.0.0.1"
    this.client = MQTT.connect(`ws://${c}:9001`);
    this.client.subscribe("device_beacon");
    this.client.on("message", this.handleMessage.bind(this));
    this.send_intervals = {};
  }
  init(store) {
    this.store = store;
  }
  handleMessage(topic, payload) {
    const t = topic.split("/");
    if(t[0] === "device_beacon") {
      this.handleDeviceBeacon(t, payload);
    } else if (t[1] === "camera_stream") {
      this.handleCameraStream(t, payload);
    } else if (t[1] === "telemetry") {
      this.handleDeviceTelemetry(t, payload);
    } else if (t[1] === "conf") {
      this.handleDeviceConf(t, payload);
    } else if (t[1] === "setconf") {
      // ignored
    } else {
      console.warn("Unhandled MQTT topic:", topic);
    }
  }
  handleDeviceBeacon(topic, payload) {
    this.client.subscribe(`${payload}/#`);
    if(this.store) {
      this.store.dispatch(newDevice(payload.toString()));
    }
  }
  handleCameraStream(topic, payload) {
    const device_id = topic[0];
    const stream = topic.slice(1).join("/");
    if(this.store) {
      this.store.dispatch(updateTelemetry(device_id, stream, payload.toString()));
    }
  }
  handleDeviceTelemetry(topic, payload) {
    const device_id = topic[0];
    const telemetry = topic.slice(2).join("/");
    if(this.store) {
      this.store.dispatch(updateTelemetry(device_id, telemetry, payload.toString()));
    }
  }
  handleDeviceConf(topic, payload) {
    const device_id = topic[0];
    const conf = topic.slice(1).join("/");
    if(this.store) {
      this.store.dispatch(updateTelemetry(device_id, conf, payload.toString()));
    }
  }
  sendOnce(topic, payload, qos=2) {
    console.log("Sending to", topic);
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
