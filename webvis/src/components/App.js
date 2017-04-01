import React, { Component } from 'react';
import './App.css';
import DeviceList from '../containers/DeviceList';
import Device from '../containers/Device';

class App extends Component {
  render() {
    return (
      <div style={{ paddingLeft: "256px" }}>
        <DeviceList />
        <div className="App-content">
          <Device />
        </div>
      </div>
    );
  }
}

export default App;
