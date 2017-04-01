import React, { Component } from 'react';
import MQTT from 'mqtt';
import logo from './logo.svg';
import './App.css';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = { messages: [] };
  }
  componentDidMount() {
    this.client = MQTT.connect("ws://localhost:9001");
    this.client.subscribe("#");
    this.client.on("message", (topic, payload) => {
        this.setState({
            messages: this.state.messages.concat({ topic, payload })
        });
    });
  }
  render() {
    let rows = this.state.messages.map((m) => {
        return <pre key={m.payload.toString()}>{m.topic} {m.payload.toString()}</pre>;
    });

    return (
      <div className="App">
        <div className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h2>Welcome to React</h2>
        </div>
        {rows}
      </div>
    );
  }
}

export default App;
