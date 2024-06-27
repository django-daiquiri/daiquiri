import React, { useState } from 'react'

import { parseLocation, updateLocation } from '../utils/location'

import Form from './Form'
import Forms from './Forms'
import Job from './Job'
import Jobs from './Jobs'
import Status from './Status'

const App = () => {
  const location = parseLocation()

  const [state, setState] = useState(location)

  const loadJob = (jobId) => {
    updateLocation({ jobId })
    setState({ jobId })
  }

  const loadForm = (formKey) => {
    updateLocation({ formKey })
    setState({ formKey })
  }

  return (
    <div>
      <h1 className="mb-4">Query interface</h1>

      <div className="row">
        <div className="col-lg-3 order-2 order-lg-1">
          <Status />
          <Forms formKey={state.formKey} loadForm={loadForm} />
          <Jobs jobId={state.jobId} loadJob={loadJob} />
        </div>
        <div className="col-lg-9 order-1 order-lg-2">
          {
            state.jobId && <Job jobId={state.jobId} />
          }
          {
            state.formKey && <Form formKey={state.formKey} />
          }
        </div>
      </div>
    </div>
  )
}

export default App
