import React, { Component } from 'react';
import Gauge from './Gauge';
import DeviceConfig from '../containers/DeviceConfig';
import DeviceCams from './DeviceCams';

class Device extends Component {
  getVoltages() {
    const unit = "V";
    const voltages = [
      {
        name: "Cell1",
        value: parseFloat(this.props.device["voltage/cell1"]).toFixed(1),
        danger: 4.2,
        warn: 3.9,
        unit
      },
      {
        name: "Cell2",
        value: parseFloat(this.props.device["voltage/cell2"]).toFixed(1),
        danger: 4.2,
        warn: 3.9,
        unit
      },
      {
        name: "Battery",
        value: parseFloat(this.props.device["voltage/battery"]).toFixed(1),
        danger: 2*4.2,
        warn: 2*3.9,
        unit
      },
      {
        name: "3v3 bus",
        value: parseFloat(this.props.device["voltage/3v3bus"]).toFixed(1),
        danger: 4,
        warn: 3.5,
        unit
      },
      {
        name: "Vcc",
        value: parseFloat(this.props.device["voltage/vcc"]).toFixed(1),
        danger: 6,
        warn: 5.5,
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
          danger={s.danger}
          warn={s.warn}
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
        value: parseFloat(this.props.device["temperature/ambient"]).toFixed(1),
        danger: 60,
        warn: 40,
        unit
      },
      {
        name: "Motor",
        value: parseFloat(this.props.device["temperature/motor"]).toFixed(1),
        danger: 60,
        warn: 40,
        unit
      },
      {
        name: "ESC",
        value: parseFloat(this.props.device["temperature/esc"]).toFixed(1),
        danger: 60,
        warn: 40,
        unit
      },
      {
        name: "Battery",
        value: parseFloat(this.props.device["temperature/battery"]).toFixed(1),
        danger: 60,
        warn: 40,
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
        value: parseFloat(this.props.device["accelX"]).toFixed(1),
        danger: Infinity,
        warn: Infinity,
        unit
      },
      {
        name: "AccelY",
        value: parseFloat(this.props.device["accelY"]).toFixed(1),
        danger: Infinity,
        warn: Infinity,
        unit
      },
      {
        name: "AccelZ",
        value: parseFloat(this.props.device["accelZ"]).toFixed(1),
        danger: Infinity,
        warn: Infinity,
        unit
      },
    ];
    return this.getRow(accels);
  }
  getMisc() {
    const unit = "";
    const misc = [
      {
        name: "Speed",
        value: this.props.device["speed"],
        danger: Infinity,
        warn: Infinity,
        unit
      },
      {
        name: "Engine power",
        value: parseFloat(this.props.device["enginePower"]).toFixed(1),
        danger: Infinity,
        warn: Infinity,
        unit
      },
      {
        name: "Steering Angle",
        value: parseFloat(this.props.device["steeringAngle"]).toFixed(1),
        danger: Infinity,
        warn: Infinity,
        unit: "°"
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
      <h1>Config</h1>
        <DeviceConfig device={this.props.device} />
      <h1>Cams</h1>
        <DeviceCams device={this.props.device} />
      <h1>Debug</h1>
        <pre>{JSON.stringify(this.props.device, null, 4)}</pre>
      </div>
    );
  }
}

export default Device;
