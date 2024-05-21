import React from 'react'

import { parseLocation } from '../utils/location'

import Forms from './Forms'
import Jobs from './Jobs'
import Status from './Status'

const App = () => {
  const { jobId, formKey } = parseLocation()

  return (
    <div className="container">
      <h1 className="mb-4">Query interface</h1>

      <div className="row">
        <div className="col-sm-4">
          <Status />
          <Forms />
          <Jobs />
        </div>
        <div className="col-sm-8">
          {
            jobId && <pre>{jobId}</pre>
          }
          {
            formKey && <pre>{formKey}</pre>
          }
        </div>
      </div>
    </div>
  )
}

export default App
