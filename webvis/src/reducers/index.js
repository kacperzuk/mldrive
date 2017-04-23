import { combineReducers } from 'redux';
import devices from './devices';
import uistate from './uistate';
import gamepad from './gamepad';

const reducer = combineReducers({
  devices,
  uistate,
  gamepad
});

export default reducer;
