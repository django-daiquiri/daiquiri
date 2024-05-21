import React from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { useJobsQuery } from '../hooks/query'
import { basePath } from '../utils/location'

import Loading from './Loading'

const Jobs = ({ loadJob }) => {
  const { data: jobs } = useJobsQuery()

  const handleLoadJob = (event, job) => {
    event.preventDefault()
    loadJob(job.id)
  }

  return (
    <div className="card mb-3">
      <div className="card-header">
        {gettext('Job list')}
      </div>
      {
        isNil(jobs) ? (
          <div className="card-body">
            <Loading />
          </div>
        ) : (
          <ul className="list-group list-group-flush">
            {
              jobs.map((job) => (
                <li key={job.id} className="list-group-item">
                  <a href={`${basePath}/${job.id}/`} onClick={(event) => handleLoadJob(event, job)}>
                    {job.table_name}
                  </a>
                </li>
              ))
            }
          </ul>
        )
      }
    </div>
  )
}

Jobs.propTypes = {
  loadJob: PropTypes.func.isRequired
}

export default Jobs
