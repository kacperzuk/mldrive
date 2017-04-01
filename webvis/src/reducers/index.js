import { combineReducers } from 'redux';
import devices from './devices';
import uistate from './uistate';

const reducer = combineReducers({
  devices,
  uistate
});

export default reducer;
