import React, { useState } from 'react'

import { parseLocation, updateLocation } from '../utils/location'

import Jobs from './Jobs'
import Submit from './Submit'

const Query = () => {
  const location = parseLocation()

  const [state, setState] = useState(location)

  const loadJobs = () => {
    updateLocation({ jobs: true })
    setState({ jobs: true })
  }

  const loadJob = (jobId) => {
    updateLocation({ jobId })
    setState({ jobId })
  }

  const loadForm = (formKey, query = null) => {
    updateLocation({ formKey })
    setState({ formKey, query })
  }

  return state.jobs ? (
    <Jobs
      loadForm={loadForm}
      loadJob={loadJob}
    />
  ) : (
    <Submit
      formKey={state.formKey}
      jobId={state.jobId}
      query={state.query}
      loadJobs={loadJobs}
      loadJob={loadJob}
      loadForm={loadForm}
    />
  )
}

export default Query
