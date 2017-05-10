import React, { Component } from 'react';

class DeviceCams extends Component {
  handleRef(ref) {
    if(this.unmounting || !ref) return;
    ref.onload = () => {
      this.handleRef(ref);
    };
    ref.onerror = () => {
      setTimeout(() => {
        this.handleRef(ref);
      }, 500);
    };
    ref.src = this.props.device["camera_stream/0"] + "?" + Date.now();
  }
  componentWillUnmount() {
    this.unmounting = true;
  }
  shouldComponentUpdate(prevProps) {
    return prevProps.device["camera_stream/0"] !== this.props.device["camera_stream/0"];
  }
  render() {
    if(!this.props.device["camera_stream/0"]) {
      return null;
    }

    return (
      <img alt="" ref={this.handleRef.bind(this)} />
    );
  }
}

export default DeviceCams;
