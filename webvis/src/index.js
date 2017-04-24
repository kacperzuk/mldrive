import React from 'react';
import ReactDOM from 'react-dom';
import { createStore } from 'redux'
import { batchedSubscribe } from 'redux-batched-subscribe';
import debounce from 'lodash.debounce';
import { Provider } from 'react-redux'
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import injectTapEventPlugin from 'react-tap-event-plugin';
injectTapEventPlugin();

import App from './components/App';
import reducer from './reducers';
import connector from './connector';
import controller from './controller';

import './index.css';

const debounceNotify = debounce(notify => notify(), 10);
const store = createStore(reducer, undefined, batchedSubscribe(debounceNotify));
connector.init(store);
controller.init(store);

ReactDOM.render(
  <Provider store={store}>
    <MuiThemeProvider>
      <App/>
    </MuiThemeProvider>
  </Provider>,
  document.getElementById('root')
);
