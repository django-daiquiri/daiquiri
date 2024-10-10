import React, { useState } from 'react'

import { parseLocation, updateLocation } from '../utils/location'

import Form from './forms/Form'
import Forms from './Forms'
import FormSql from './forms/FormSql'
import FormUpload from './forms/FormUpload'
import Job from './job/Job'
import Jobs from './Jobs'
import Status from './Status'

const App = () => {
  const location = parseLocation()

  const [state, setState] = useState(location)

  const getForm = () => {
    switch (state.formKey) {
      case 'sql':
        return <FormSql formKey={state.formKey} loadJob={loadJob} query={state.query} />
      case 'upload':
        return <FormUpload formKey={state.formKey} loadJob={loadJob} />
      default:
        return <Form formKey={state.formKey} loadJob={loadJob} />
    }
  }

  const loadJob = (jobId) => {
    updateLocation({ jobId })
    setState({ jobId })
  }

  const loadForm = (formKey, query = null) => {
    updateLocation({ formKey })
    setState({ formKey, query })
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
            state.jobId && <Job jobId={state.jobId} loadForm={loadForm} />
          }
          {
            state.formKey && getForm()
          }
        </div>
      </div>
    </div>
  )
}

export default App
