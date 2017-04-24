const devices = (state = {}, action) => {
  switch (action.type) {
    case 'NEW_DEVICE':
      if (state[action.device_id]) {
        return state;
      } else {
        return {
          ...state,
          [action.device_id]: {
            id: action.device_id,
            dirty_conf: false
          }
        };
      }
    case 'UPDATE_FORM':
      return {
        ...state,
        [action.device_id]: {
          ...state[action.device_id],
          dirty_conf: true,
          [action.field]: action.value
        }
      };
    case 'UPDATE_TELEMETRY':
      if (action.telemetry.indexOf("conf") === 0 && state[action.device_id].dirty_conf) {
        return state;
      }

      return {
        ...state,
        [action.device_id]: {
          ...state[action.device_id],
          [action.telemetry]: action.value
        }
      };
    case 'CLEAR_FORM':
      return {
        ...state,
        [action.device_id]: {
          ...state[action.device_id],
          dirty_conf: false
        }
      };

    default:
      return state;
  }
}

export default devices;
