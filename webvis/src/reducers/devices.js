const devices = (state = {}, action) => {
  switch (action.type) {
    case 'NEW_DEVICE':
      return {
        ...state,
        [action.device_id]: {}
      };
    case 'UPDATE_TELEMETRY':
      return {
        ...state,
        [action.device_id]: {
          ...state[action.device_id],
          [action.telemetry]: action.value
        }
      };
    default:
      return state
  }
}

export default devices
