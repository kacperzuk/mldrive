import React, { Component } from 'react';
import 'jsmpeglive/dist/jsmpeglive-bundle';
import jsmpeglive from 'exports?jsmpeglive!jsmpeglive/dist/jsmpeglive-bundle.js'; // eslint-disable-line

class DeviceCams extends Component {
  handleCanvasRef(ref) {
    if(this.socket) {
      this.socket.close();
    }
    this.player = new jsmpeglive({canvas: ref});
    this.socket = new WebSocket("ws://127.0.0.1:8084/");
    this.socket.addEventListener('message', (event) => {
      const reader = new FileReader();
      reader.addEventListener("loadend", () => {
        this.player.render(reader.result);
      });
      reader.readAsArrayBuffer(event.data);
    });
  }
  componentWillUnmount() {
    if(this.socket) {
      this.socket.close();
    }
  }
  shouldComponentUpdate(prevProps) {
    return prevProps.device["camera_stream/0"] !== this.props.device["camera_stream/0"];
  }
  render() {
    if(!this.props.device["camera_stream/0"]) {
      return null;
    }

    return (
      <canvas width={320} height={240} ref={this.handleCanvasRef.bind(this)} />
    );
  }
}

export default DeviceCams;
