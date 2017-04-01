import React, { Component } from 'react';
import GaugeAnimated from 'gauge-animated';

class Gauge extends Component {
  componentDidMount() {
    this.gauge = new GaugeAnimated(this.div, this.props);
    this.gauge.setTarget(this.props.value);
  }
  componentDidUpdate(prevProps) {
    if (prevProps.value !== this.props.value) {
      this.gauge.setTarget(this.props.value);
    }
  }
  render() {
    return <div ref={(ref) => { this.div = ref }} />;
  }
}

export default Gauge;
