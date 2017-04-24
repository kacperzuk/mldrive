import { connect } from 'react-redux';
import { updateForm, clearForm } from '../actions';
import DeviceConfigView from '../components/DeviceConfig';

import connector from '../connector';
import { itom } from '../utils';

const mapStateToProps = (state, ownProps) => ({
  device: ownProps.device,
});

const mapDispatchToProps = (dispatch, ownProps) => ({
  setConf(topic, val) {
    const device_id = ownProps.device.id;
    dispatch(updateForm(device_id, `conf/${topic}`, val));
  },
  submit() {
    const device_id = ownProps.device.id;
    Object.keys(ownProps.device).filter((k) => k.indexOf("conf") === 0).forEach((topic) => {
      let val = ownProps.device[topic];
      if (!isNaN(parseFloat(val)) && isFinite(val)) {
        val = itom(val);
      }
      if(topic.indexOf("conf/vision/") === 0) {
        connector.sendOnce(`${device_id}/set${topic}`, val);
      } else {
        connector.sendOnce(`${device_id}/${topic}`, val);
      }
    });
    dispatch(clearForm(device_id));
  },
  clear() {
    const device_id = ownProps.device.id;
    dispatch(clearForm(device_id));
  }
});

const DeviceConfig = connect(mapStateToProps, mapDispatchToProps)(DeviceConfigView);

export default DeviceConfig;
