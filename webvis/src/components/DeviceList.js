import React, { Component } from 'react';

class DeviceList extends Component {
  render() {
    return (
      <ul>
        {Object.keys(this.props.devices).map((device) => (
          <li key={device} onClick={() => this.props.showDevice(device)}>#{device}</li>
        ))}
      </ul>
    );
  }
}

export default DeviceList;
