import React, { Component } from 'react';

class Device extends Component {
  render() {
    return (
      <pre>{JSON.stringify(this.props.device, null, 4)}</pre>
    );
  }
}

export default Device;
