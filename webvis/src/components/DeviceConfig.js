import React, { Component } from 'react';
import Toggle from 'material-ui/Toggle';
import TextField from 'material-ui/TextField';

import './DeviceConfig.css';


class DeviceConfig extends Component {
  render() {
    return (
      <div className="controls">
        <div style={{ maxWidth: "200px" }}>
        <Toggle
          label="Debug"
          toggled={(!!this.props.device["conf/debug"]) || false}
          onToggle={(event, toggled) => {
            this.props.setDebug(toggled);
          }}/>
        </div>
        <div>
        <TextField
          className="smallcontrol"
          type="number"
          floatingLabelText="Throttle delay"
          value={this.props.device["conf/throttle_delay"] || ""}
          onChange={(event) => {
            this.props.setThrottleDelay(event.target.value);
          }}/>
        <TextField
          className="smallcontrol"
          type="number"
          floatingLabelText="Throttle middle"
          value={this.props.device["conf/throttle_middle"] || ""}
          onChange={(event) => {
            this.props.setThrottleMiddle(event.target.value);
          }}/>
        </div>
        <div>
        <TextField
          className="smallcontrol"
          type="number"
          floatingLabelText="Steering delay"
          value={this.props.device["conf/steering_delay"] || ""}
          onChange={(event) => {
            this.props.setSteeringDelay(event.target.value);
          }}/>
        <TextField
          className="smallcontrol"
          type="number"
          floatingLabelText="Steering min"
          value={this.props.device["conf/steering_min"] || ""}
          onChange={(event) => {
            this.props.setSteeringMin(event.target.value);
          }}/>
        <TextField
          className="smallcontrol"
          type="number"
          floatingLabelText="Steering middle"
          value={this.props.device["conf/steering_middle"] || ""}
          onChange={(event) => {
            this.props.setSteeringMiddle(event.target.value);
          }}/>
        <TextField
          className="smallcontrol"
          type="number"
          floatingLabelText="Steering max"
          value={this.props.device["conf/steering_max"] || ""}
          onChange={(event) => {
            this.props.setSteeringMax(event.target.value);
          }}/>
        </div>
      </div>
    );
  }
}

export default DeviceConfig;
