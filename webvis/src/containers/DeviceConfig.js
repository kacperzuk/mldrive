import { connect } from 'react-redux';
import { updateTelemetry } from '../actions';
import DeviceConfigView from '../components/DeviceConfig';

import connector from '../connector';
import { itom } from '../utils';

const mapStateToProps = (state, ownProps) => ({
  device: ownProps.device,
});

const mapDispatchToProps = (dispatch, ownProps) => ({
  setDebug(debug) {
    const device_id = ownProps.device.id;
    connector.sendOnce(`${device_id}/conf/debug`, debug ? 1 : 0);
    dispatch(updateTelemetry(device_id, "conf/debug", debug ? 1 : 0));
  },
  setThrottleDelay(val) {
    const device_id = ownProps.device.id,
          delay = itom(val);
    connector.sendOnce(`${device_id}/conf/throttle_delay`, delay);
    dispatch(updateTelemetry(device_id, "conf/throttle_delay", val));
  },
  setThrottleMiddle(val) {
    const device_id = ownProps.device.id,
          middle = itom(val);
    connector.sendOnce(`${device_id}/conf/throttle_middle`, middle);
    dispatch(updateTelemetry(device_id, "conf/throttle_middle", val));
  },
  setSteeringDelay(val) {
    const device_id = ownProps.device.id,
          delay = itom(val);
    connector.sendOnce(`${device_id}/conf/steering_delay`, delay);
    dispatch(updateTelemetry(device_id, "conf/steering_delay", val));
  },
  setSteeringMin(val) {
    const device_id = ownProps.device.id,
          min = itom(val);
    connector.sendOnce(`${device_id}/conf/steering_min`, min);
    dispatch(updateTelemetry(device_id, "conf/steering_min", val));
  },
  setSteeringMiddle(val) {
    const device_id = ownProps.device.id,
          middle = itom(val);
    connector.sendOnce(`${device_id}/conf/steering_middle`, middle);
    dispatch(updateTelemetry(device_id, "conf/steering_middle", val));
  },
  setSteeringMax(val) {
    const device_id = ownProps.device.id,
          max = itom(val);
    connector.sendOnce(`${device_id}/conf/steering_max`, max);
    dispatch(updateTelemetry(device_id, "conf/steering_max", val));
  }
});

const DeviceConfig = connect(mapStateToProps, mapDispatchToProps)(DeviceConfigView);

export default DeviceConfig;
