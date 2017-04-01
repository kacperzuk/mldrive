import React, { Component } from 'react';

class DeviceList extends Component {
  render() {
    return (
      <pre>Known devices: {JSON.stringify(this.props.devices, null, 4)}</pre>
    );
  }
}

export default DeviceList;
