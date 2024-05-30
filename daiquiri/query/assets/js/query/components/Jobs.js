import React, { useState } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { isEmpty, isNil } from 'lodash'

import { baseUrl } from '../../../../../core/assets/js/utils/location'

import { useJobsQuery } from '../hooks/query'
import { basePath } from '../utils/location'

import Loading from './Loading'

const Jobs = ({ jobId, loadJob }) => {
  const { data: jobs } = useJobsQuery()

  const [open, setOpen] = useState([''])

  const handleLoadJob = (event, job) => {
    event.preventDefault()
    loadJob(job.id)
  }

  const toggleRunId = (runId) => {
    setOpen(open.includes(runId) ? open.filter((entry) => entry !== runId) : [...open, runId])
  }

  // sort jobs according to their run id
  const runIds = isNil(jobs) ? [] : jobs.reduce((runIds, job) => {
    return runIds.includes(job.run_id) ? runIds : [...runIds, job.run_id]
  }, []).sort((a, b) => {
    // sort and put the empty runId at the end
    if (isEmpty(a)) {
      return 1
    } else if (isEmpty(b)) {
      return -1
    } else {
      return (a < b) ? -1 : 1
    }
  })

  return (
    <div className="jobs card card-nav mb-3">
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
              runIds.map((runId) => (
                <React.Fragment key={runId}>
                  {
                    runIds.length > 1 && (
                      <li key={runId} className="list-group-item">
                        <button type="button" className="btn btn-link" onClick={() => toggleRunId(runId)}>
                          <div className="d-flex align-items-center">
                            {isEmpty(runId) ? gettext('No run id') : interpolate(gettext('Run id: %s'), [runId])}
                            <span className="ms-auto material-symbols-rounded">
                              {open.includes(runId) ? 'folder_open' : 'folder'}
                            </span>
                          </div>
                        </button>
                      </li>
                    )
                  }
                  {
                    open.includes(runId) && (
                      jobs.filter((job) => job.run_id === runId).map((job) => (
                        <li key={job.id} className={classNames({
                          'list-group-item': true,
                          'active': job.id === jobId
                        })}>
                          <a href={`${basePath}/${job.id}/`} onClick={(event) => handleLoadJob(event, job)}>
                            {job.table_name}
                          </a>
                        </li>
                      ))
                    )
                  }
                </React.Fragment>
              ))
            }
          </ul>
        )
      }
      <div className="card-footer">
        <a href={`${baseUrl}/query/jobs/new/`} target="_blank" rel="noreferrer">
          {gettext('View verbose job list')}
        </a>
      </div>
    </div>
  )
}

Jobs.propTypes = {
  jobId: PropTypes.string,
  loadJob: PropTypes.func.isRequired
}

export default Jobs
