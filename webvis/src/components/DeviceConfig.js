import React, { Component } from 'react';
import Toggle from 'material-ui/Toggle';
import TextField from 'material-ui/TextField';
import SelectField from 'material-ui/SelectField';
import MenuItem from 'material-ui/MenuItem';
import RaisedButton from 'material-ui/RaisedButton';
import { itom } from '../utils';

import './DeviceConfig.css';


class DeviceConfig extends Component {
  render() {
    return (
      <div className="controls">
        Form state: {this.props.device["dirty_conf"] ? "dirty!" : "clean"}
        <h2>Vision</h2>
        <div>
          <SelectField
            floatingLabelText="Output mode"
            value={this.props.device["conf/vision/output_mode"] || ""}
            className="smallcontrol"
            onChange={(event,index,value) => {
              this.props.setConf("vision/output_mode", value);
            }}>
            <MenuItem value="original" primaryText="Original" />
            <MenuItem value="mask" primaryText="Area of interest mask" />
            <MenuItem value="masked" primaryText="Masked image" />
            <MenuItem value="canny" primaryText="Canny edge detection" />
            <MenuItem value="hough" primaryText="Hough line detection" />
            <MenuItem value="final" primaryText="Final lane" />
          </SelectField>
      </div>
      <div>
          <TextField
            className="smallcontrol"
            type="number"
            floatingLabelText="Canny low threshold"
            value={this.props.device["conf/vision/canny/low"] || ""}
            onChange={(event) => {
              this.props.setConf("vision/canny/low", event.target.value);
            }}/>
          <TextField
            className="smallcontrol"
            type="number"
            floatingLabelText="Canny high threshold"
            value={this.props.device["conf/vision/canny/high"] || ""}
            onChange={(event) => {
              this.props.setConf("vision/canny/high", event.target.value);
            }}/>
        </div>
        <div>
          <TextField
            className="smallcontrol"
            type="number"
            floatingLabelText="Hough intersections"
            value={this.props.device["conf/vision/hough/intersections"] || ""}
            onChange={(event) => {
              this.props.setConf("vision/hough/intersections", event.target.value);
            }}/>
          <TextField
            className="smallcontrol"
            type="number"
            floatingLabelText="Hough min line length"
            value={this.props.device["conf/vision/hough/min_length"] || ""}
            onChange={(event) => {
              this.props.setConf("vision/hough/min_length", event.target.value);
            }}/>
          <TextField
            className="smallcontrol"
            type="number"
            floatingLabelText="Hough max gap"
            value={this.props.device["conf/vision/hough/max_gap"] || ""}
            onChange={(event) => {
              this.props.setConf("vision/hough/max_gap", event.target.value);
            }}/>
        </div>
        <div>
          <TextField
            className="smallcontrol"
            type="number"
            floatingLabelText="Lane detect height"
            value={this.props.device["conf/vision/lane_detect_height"] || ""}
            onChange={(event) => {
              this.props.setConf("vision/lane_detect_height", event.target.value);
            }}/>
          <TextField
            className="smallcontrol"
            type="number"
            floatingLabelText="Line merge distance"
            value={this.props.device["conf/vision/line_merge_distance"] || ""}
            onChange={(event) => {
              this.props.setConf("vision/line_merge_distance", event.target.value);
            }}/>
          <TextField
            className="smallcontrol"
            type="number"
            min="0.1"
            max="0.99"
            step="0.05"
            floatingLabelText="Line smoothing"
            value={this.props.device["conf/vision/line_smoothing"] || ""}
            onChange={(event) => {
              this.props.setConf("vision/line_smoothing", parseFloat(event.target.value));
            }}/>
        </div>
        <h2>Vehicle</h2>
        <div style={{ maxWidth: "200px" }}>
        <Toggle
          label="Debug"
          toggled={(!!this.props.device["conf/debug"]) || false}
          onToggle={(event, toggled) => {
            this.props.setConf("conf/debug", toggled ? 1 : 0);
          }}/>
        </div>
        <div>
        <TextField
          className="smallcontrol"
          type="number"
          floatingLabelText="Throttle delay"
          value={this.props.device["conf/throttle_delay"] || ""}
          onChange={(event) => {
            this.props.setConf("throttle_delay", itom(event.target.value));
          }}/>
        <TextField
          className="smallcontrol"
          type="number"
          floatingLabelText="Throttle middle"
          value={this.props.device["conf/throttle_middle"] || ""}
          onChange={(event) => {
            this.props.setConf("throttle_middle", itom(event.target.value));
          }}/>
        </div>
        <div>
        <TextField
          className="smallcontrol"
          type="number"
          floatingLabelText="Steering delay"
          value={this.props.device["conf/steering_delay"] || ""}
          onChange={(event) => {
            this.props.setConf("steering_delay", itom(event.target.value));
          }}/>
        <TextField
          className="smallcontrol"
          type="number"
          floatingLabelText="Steering min"
          value={this.props.device["conf/steering_min"] || ""}
          onChange={(event) => {
            this.props.setConf("steering_min", itom(event.target.value));
          }}/>
        <TextField
          className="smallcontrol"
          type="number"
          floatingLabelText="Steering middle"
          value={this.props.device["conf/steering_middle"] || ""}
          onChange={(event) => {
            this.props.setConf("steering_middle", itom(event.target.value));
          }}/>
        <TextField
          className="smallcontrol"
          type="number"
          floatingLabelText="Steering max"
          value={this.props.device["conf/steering_max"] || ""}
          onChange={(event) => {
            this.props.setConf("steering_max", itom(event.target.value));
          }}/>
        </div>
        <RaisedButton label="Clear" primary={true} onClick={this.props.clear} style={{margin: "1em"}} />
        <RaisedButton label="Submit!" primary={true} onClick={this.props.submit} style={{margin: "1em"}} />
      </div>
    );
  }
}

export default DeviceConfig;
