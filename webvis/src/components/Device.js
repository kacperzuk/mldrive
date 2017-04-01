import React, { Component } from 'react';
import DeviceTempVis from './DeviceTempVis';

class Device extends Component {
  render() {
    if(!this.props.device) {
      return null;
    }

    return (
      <div>
        <pre>{JSON.stringify(this.props.device, null, 4)}</pre>
        <DeviceTempVis device={this.props.device} />
      </div>
    );
  }
}

export default Device;
