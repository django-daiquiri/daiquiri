import React from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'
import { useJobQuery } from '../hooks/query'

const Job = ({ jobId }) => {
  const { data: job } = useJobQuery(jobId)

  return isNil(job) ? (
      <span>{gettext('Loading ...')}</span>
    ) : (
    <div className="job">
      <h2>{job.table_name}</h2>
      <pre>{job.id}</pre>
      <pre>{job.query}</pre>
    </div>
  )
}

Job.propTypes = {
  jobId: PropTypes.string.isRequired
}

export default Job
