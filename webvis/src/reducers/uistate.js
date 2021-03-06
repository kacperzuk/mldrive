const uistate = (state = {}, action) => {
  switch (action.type) {
    case 'NEW_DEVICE':
      if (!state.visible_device) {
        return {
          ...state,
          visible_device: action.device_id
        };
      } else {
        return state;
      }
    case 'SET_VISIBLE_DEVICE':
      return {
        ...state,
        visible_device: action.device_id
      };
    default:
      return state
  }
}

export default uistate;
