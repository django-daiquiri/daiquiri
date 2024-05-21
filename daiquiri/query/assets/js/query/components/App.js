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
    <div className="container">
      <h1 className="mb-4">Query interface</h1>

      <div className="row">
        <div className="col-sm-4">
          <Status />
          <Forms loadForm={loadForm} />
          <Jobs loadJob={loadJob} />
        </div>
        <div className="col-sm-8">
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
