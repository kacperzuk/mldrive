import React, { Component } from 'react';
import Drawer from 'material-ui/Drawer';
import MenuItem from 'material-ui/MenuItem';

class DeviceList extends Component {
  getMenuItems() {
    if (Object.keys(this.props.devices).length === 0) {
      return <MenuItem disabled={true}>No devices discovered yet :(</MenuItem>;
    }

    return Object.keys(this.props.devices).map((device) => (
      <MenuItem
        key={device}
        onTouchTap={() => this.props.showDevice(device)} >
        Device #{device}
      </MenuItem>
    ));
  }
  render() {
    return (
      <Drawer
        docked={true}
        open={true}>
        {this.getMenuItems()}
      </Drawer>
    );
  }
}

export default DeviceList;
