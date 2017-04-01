import { connect } from 'react-redux';
import DeviceListView from '../components/DeviceList';

const mapStateToProps = (state, ownProps) => ({
  devices: state.devices
});

const DeviceList = connect(mapStateToProps)(DeviceListView);

export default DeviceList;
