/* import React from 'react';
 * import ReactDOM from 'react-dom';
 * import './index.css';
 * import App from './App';
 * import registerServiceWorker from './registerServiceWorker';
 * 
 * ReactDOM.render(<App />, document.getElementById('root'));
 * registerServiceWorker();*/

import registerServiceWorker from './registerServiceWorker'
import React from 'react'
import { render } from 'react-dom'
import Root from './containers/Root'

registerServiceWorker();

render(
  <Root />,
  document.getElementById('root')
)
