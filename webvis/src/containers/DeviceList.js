import { connect } from 'react-redux';
import { setVisibleDevice } from '../actions';
import DeviceListView from '../components/DeviceList';

const mapStateToProps = (state, ownProps) => ({
  devices: state.devices
});

const mapDispatchToProps = (dispatch, ownProps) => ({
  showDevice(device_id) {
    dispatch(setVisibleDevice(device_id));
  }
});

const DeviceList = connect(mapStateToProps, mapDispatchToProps)(DeviceListView);

export default DeviceList;
