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
          }
        };
      }
    case 'UPDATE_TELEMETRY':
      let n = {
        ...state,
        [action.device_id]: {
          ...state[action.device_id],
          [action.telemetry]: action.value
        }
      };
      return n;
    default:
      return state
  }
}

export default devices
