import React, { Component } from 'react';
import Gauge from './Gauge';

class DeviceTempVis extends Component {
  getTemp(source) {
    const t = parseInt(this.props.device[`temperature/${source}`], 10)/10;
    if(isNaN(t)) {
      return null;
    }

    return <div style={{ textAlign: "center", width: "140px", display: "inline-block", margin: "0 10px" }}>
      <Gauge
          size={140}
          startAngle={Math.PI}
          stopAngle={Math.PI*2}
          needleAngleMin={Math.PI*0.9}
          needleAngleMax={Math.PI*2.1}
          labelSteps={5}
          stopPinColor={0}
          // markerLength={5}
          markerWidth={1}
          valueDisplay={true}
          valueDisplayPostfix={`&deg;C<br>${source}`}
          // valueCallback={v => v3.innerHTML = v.toFixed(1)}
          min={-15}
          max={45}
          stepValue={2}
          mediumSteps={5}
          largeSteps={20}
          labelRadius={0.65}
          // font={'22px arial'}
          // faceText={'&deg;C'}
          value={t}
        />
      </div>;
  }
  render() {
    return (
      <div style={{ display: "flex", justifyContent: "space-around" }}>
        {this.getTemp("ambient")}
        {this.getTemp("motor")}
        {this.getTemp("esc")}
        {this.getTemp("battery")}
      </div>
    );
  }
}

export default DeviceTempVis;
