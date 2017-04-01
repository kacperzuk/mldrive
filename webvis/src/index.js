import React from 'react';
import ReactDOM from 'react-dom';
import { createStore } from 'redux'
import { Provider } from 'react-redux'

import App from './components/App';
import reducer from './reducers';
import connector from './connector';

import './index.css';

const store = createStore(reducer);
new connector(store);

ReactDOM.render(
  <Provider store={store}>
    <App />
  </Provider>,
  document.getElementById('root')
);
