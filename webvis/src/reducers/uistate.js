const uistate = (state = {}, action) => {
  switch (action.type) {
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
