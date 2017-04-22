import React, { Component } from 'react';
import './Gauge.css';

class Gauge extends Component {
  render() {
    const goodBgColor = "#7EBD77",
          warnBgColor = "#E7D992",
          dangBgColor = "#E79692";

    let bgColor = goodBgColor;
    if(this.props.value > this.props.dangerAbove || this.props.value < this.props.dangerBelow) {
      bgColor = dangBgColor;
    } else if (this.props.value > this.props.warningAbove || this.props.value < this.props.warningBelow) {
      bgColor = warnBgColor;
    }

    return <div style={
      {
        textAlign: "center",
        width: "140px",
        padding: "10px 0",
        display: "inline-block",
        margin: "10px",
        backgroundColor: bgColor
      }}>
        <div className="capitalize-first" style={
          {
            color: "white",
            fontSize: "0.8rem"
          }
        }>
        {this.props.name}
        </div>
        <div style={
          {
            color: "white",
            opacity: 0.8,
            fontSize: "1.2rem"
          }
        }>
        {this.props.value}{this.props.unit}
        </div>
      </div>;
  }
}

export default Gauge;
