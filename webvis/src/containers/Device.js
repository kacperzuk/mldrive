import { connect } from 'react-redux';
import DeviceView from '../components/Device';

const mapStateToProps = (state, ownProps) => ({
  device: state.devices[state.uistate.visible_device],
  gamepad: state.gamepad
});

const mapDispatchToProps = (dispatch, ownProps) => ({
});

const Device = connect(mapStateToProps, mapDispatchToProps)(DeviceView);

export default Device;
