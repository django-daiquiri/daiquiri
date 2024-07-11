import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { isEmpty, isNil } from 'lodash'

import { baseUrl, userId } from 'daiquiri/core/assets/js/utils/meta'
import { useLsState } from 'daiquiri/core/assets/js/hooks/ls'

import { useJobsQuery } from '../hooks/queries'
import { basePath } from '../utils/location'

import Loading from './Loading'

const Jobs = ({ jobId, loadJob }) => {
  const { data: jobs } = useJobsQuery()

  const [openRunIds, setOpenRunIds] = useLsState('query.openRunIds', [''])

  const handleLoadJob = (event, job) => {
    event.preventDefault()
    loadJob(job.id)
  }

  const toggleRunId = (runId) => {
    setOpenRunIds(openRunIds.includes(runId) ? openRunIds.filter((entry) => entry !== runId) : [...openRunIds, runId])
  }

  // open the run id of the selected job
  useEffect(() => {
    if (!isEmpty(jobs)) {
      const job = jobs.find((job) => job.id === jobId)
      if (job && !openRunIds.includes(job.run_id)) {
        setOpenRunIds([...openRunIds, job.run_id])
      }
    }
  }, [jobs, jobId])

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

  const jobPhaseSymbols = {
    'PENDING': 'pause_circle',
    'QUEUED': 'progress_activity',
    'EXECUTING': 'play_circle',
    'COMPLETED': 'check_circle',
    'ERROR': 'warning',
    'ABORTED': 'cancel',
    'UNKNOWN': 'help',
    'HELD': 'stop_circle',
    'SUSPENDED': 'pause_circle',
    'ARCHIVED': 'block'
  }

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
                            <span className="material-symbols-rounded ms-auto">
                              {openRunIds.includes(runId) ? 'folder_open' : 'folder'}
                            </span>
                          </div>
                        </button>
                      </li>
                    )
                  }
                  {
                    openRunIds.includes(runId) && (
                      jobs.filter((job) => job.run_id === runId).map((job) => (
                        <li key={job.id} className={classNames({
                          'list-group-item': true,
                          'active': job.id === jobId
                        })}>
                          <a href={`${basePath}/${job.id}/`} onClick={(event) => handleLoadJob(event, job)}>
                            <span className="float-end">
                              <span className="material-symbols-rounded">
                                {jobPhaseSymbols[job.phase]}
                              </span>
                            </span>
                            <span>{job.table_name}</span>
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
      {
        userId && (
          <div className="card-footer">
            <a href={`${baseUrl}/query/jobs/new/`} target="_blank" rel="noreferrer">
              {gettext('View verbose job list')}
            </a>
          </div>
        )
      }
    </div>
  )
}

Jobs.propTypes = {
  jobId: PropTypes.string,
  loadJob: PropTypes.func.isRequired
}

export default Jobs
