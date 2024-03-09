import React from 'react'
import { createRoot } from 'react-dom/client'

import App from './examples/App'

createRoot(
  document.getElementById('app')
).render(<App />)
