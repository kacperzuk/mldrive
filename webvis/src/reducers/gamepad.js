const gamepad = (state = {}, action) => {
  switch (action.type) {
    case 'UPDATE_GAMEPAD':
      let n = {
        ...state,
        steering: action.steering,
        throttle: action.throttle,
        debug: {
          id: action.debug.id,
          axes: action.debug.axes,
          buttons: action.debug.buttons.map((button) => button.value),
          mapping: action.debug.mapping,
          timestamp: action.debug.timestamp,
          connected: action.debug.connected
        }
      };
      return n;
    default:
      return state
  }
}

export default gamepad;
