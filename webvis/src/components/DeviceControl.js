import React, { Component } from 'react';
import TextField from 'material-ui/TextField';


class DeviceList extends Component {
  render() {
    return (
      <div>
        <TextField
          type="number"
          min={0}
          max={10}
          floatingLabelText="Telemetry speed"
          value={this.props.device["conf/telemetryspeed"] || ""}
          onChange={(event) => {
            this.props.setTelemetrySpeed(event.target.value);
          }}/>
      </div>
    );
  }
}

export default DeviceList;
