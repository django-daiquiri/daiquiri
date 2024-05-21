import React from 'react'
import { isNil } from 'lodash'

import { useJobsQuery } from '../hooks/query'

const Jobs = () => {
  const { data: jobs } = useJobsQuery()

  return (
    <div className="card mb-3">
      <div className="card-header">
        {gettext('Job list')}
      </div>
      {
        isNil(jobs) ? (
          <div className="card-body">
            <p>Loading ...</p>
          </div>
        ) : (
          <ul className="list-group list-group-flush">
            {
              jobs.map((job) => (
                <li key={job.id} className="list-group-item">{job.table_name}</li>
              ))
            }
          </ul>
        )
      }
    </div>
  )
}

export default Jobs
