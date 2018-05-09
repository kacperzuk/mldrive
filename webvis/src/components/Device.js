import React, { Component } from 'react';
import Gauge from './Gauge';
import DeviceConfig from '../containers/DeviceConfig';
import DeviceCams from './DeviceCams';
import ObjectDetection from './ObjectDetection';

class Device extends Component {
  getVoltages() {
    const unit = "V";
    const voltages = [
      {
        name: "Cell1",
        value: (parseFloat(this.props.device["voltage/cell1"])/1000).toFixed(2),
        dangerAbove: 4.2,
        warningAbove: Infinity,
        warningBelow: 3.75,
        dangerBelow: 2.7,
        unit
      },
      {
        name: "Cell2",
        value: (parseFloat(this.props.device["voltage/cell2"])/1000).toFixed(2),
        dangerAbove: 4.2,
        warningAbove: Infinity,
        warningBelow: 3.75,
        dangerBelow: 2.7,
        unit
      },
      {
        name: "Battery",
        value: (parseFloat(this.props.device["voltage/battery"])/1000).toFixed(2),
        dangerAbove: 2*4.2,
        warningAbove: Infinity,
        warningBelow: 2*3.75,
        dangerBelow: 2*2.7,
        unit
      },
      {
        name: "3v3 bus",
        value: (parseFloat(this.props.device["voltage/3v3bus"])/1000).toFixed(2),
        dangerAbove: 3.4,
        dangerBelow: 3.2,
        unit
      },
      {
        name: "Vcc",
        value: (parseFloat(this.props.device["voltage/vcc"])/1000).toFixed(2),
        dangerAbove: 5.5,
        dangerBelow: 4.5,
        unit
      }
    ];
    return this.getRow(voltages);
  }
  getRow(spec) {
    return <div style={{ display: "flex", justifyContent: "flex-start" }}>
      {spec.map((s) => <Gauge
          key={s.name}
          value={s.value}
          dangerAbove={s.dangerAbove}
          warningAbove={s.warningAbove}
          dangerBelow={s.dangerBelow}
          warningBelow={s.warningBelow}
          name={s.name}
          unit={s.unit} />
      )}
    </div>;
  }
  getTemps() {
    const unit = "°C";
    const temps = [
      {
        name: "Ambient",
        value: (parseFloat(this.props.device["temperature/ambient"])/10).toFixed(1),
        dangerAbove: 32,
        warningAbove: 28,
        warningBelow: 15,
        dangerBelow: 5,
        unit
      },
      {
        name: "Engine",
        value: (parseFloat(this.props.device["temperature/engine"])/10).toFixed(1),
        dangerAbove: 60,
        warningAbove: 40,
        warningBelow: 5,
        dangerBelow: 0,
        unit
      },
    ];
    return this.getRow(temps);
  }
  getAccels() {
    const unit = "G";
    const accels = [
      {
        name: "AccelX",
        value: (parseFloat(this.props.device["accelX"])/100).toFixed(1),
        dangerAbove: Infinity,
        warningAbove: Infinity,
        unit
      },
      {
        name: "AccelY",
        value: (parseFloat(this.props.device["accelY"])/100).toFixed(1),
        dangerAbove: Infinity,
        warningAbove: Infinity,
        unit
      },
      {
        name: "AccelZ",
        value: (parseFloat(this.props.device["accelZ"])/100).toFixed(1),
        dangerAbove: Infinity,
        warningAbove: Infinity,
        unit
      },
    ];
    return this.getRow(accels);
  }
  getMisc() {
    const unit = "";
    const misc = [
      {
        name: "Gear",
        value: this.props.device["speed"],
        dangerAbove: Infinity,
        warningAbove: Infinity,
        unit
      },
      {
        name: "Engine power",
        value: parseFloat(this.props.device["enginePower"]).toFixed(1),
        dangerAbove: Infinity,
        warningAbove: Infinity,
        unit
      },
      {
        name: "Steering Angle",
        value: parseFloat(this.props.device["steeringAngle"]).toFixed(1),
        dangerAbove: Infinity,
        warningAbove: Infinity,
        unit: "°"
      },
      {
        name: "Range front",
        value: parseFloat(this.props.device["rangeFront"]).toFixed(1),
        dangerBelow: 10,
        warningBelow: 30,
        unit: "cm"
      },
    ];
    return this.getRow(misc);
  }
  getVision() {
    const unit = "";
    const misc = [
      {
        name: "Vision offset",
        value: parseFloat(this.props.device["vision/center_offset"]).toFixed(0),
        dangerAbove: Infinity,
        warningAbove: Infinity,
        unit
      },
      {
        name: "Vision speed",
        value: parseFloat(this.props.device["vision/speed"]).toFixed(2),
        dangerAbove: Infinity,
        warningAbove: Infinity,
        unit
      },
      {
        name: "Vision FPS",
        value: parseFloat(this.props.device["vision/fps"]).toFixed(0),
        dangerAbove: Infinity,
        warningAbove: Infinity,
        unit
      },
      {
        name: "Vision Processing FPS",
        value: parseFloat(this.props.device["vision/processing_fps"]).toFixed(0),
        dangerAbove: Infinity,
        warningAbove: Infinity,
        unit
      },
    ];
    return this.getRow(misc);
  }
  render() {
    if(!this.props.device) {
      return null;
    }

    return (
      <div>
      <h1>Telemetry</h1>
        {this.getVoltages()}
        {this.getTemps()}
        {this.getAccels()}
        {this.getMisc()}
        {this.getVision()}
      <h1>Config</h1>
        <DeviceConfig device={this.props.device} />
      <h1>Cams</h1>
        <DeviceCams device={this.props.device} />
      <hr/>
        <ObjectDetection device={this.props.device} />
      <h1>Debug</h1>
        <pre>{JSON.stringify(this.props.device, null, 4)}</pre>
        <pre>{JSON.stringify(this.props.gamepad, null, 4)}</pre>
      </div>
    );
  }
}

export default Device;
