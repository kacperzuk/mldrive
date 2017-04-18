import { connect } from 'react-redux';
import { updateTelemetry } from '../actions';
import DeviceControlView from '../components/DeviceControl';

import connector from '../connector';
import { itom } from '../utils';

const mapStateToProps = (state, ownProps) => ({
  device: ownProps.device,
});

const mapDispatchToProps = (dispatch, ownProps) => ({
  setTelemetrySpeed(speed) {
    const device_id = ownProps.device.id,
          s = itom(speed);
    connector.sendOnce(`/${device_id}/conf/telemetryspeed`, s);
    dispatch(updateTelemetry(device_id, "conf/telemetryspeed", s));
  }
});

const DeviceControl = connect(mapStateToProps, mapDispatchToProps)(DeviceControlView);

export default DeviceControl;
