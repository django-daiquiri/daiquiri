import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { isEmpty, isNil } from 'lodash'

import { userId } from 'daiquiri/core/assets/js/utils/meta'
import { useLsState } from 'daiquiri/core/assets/js/hooks/ls'

import { jobPhaseIcons, jobPhaseSpinner } from 'daiquiri/query/assets/js/constants/job'
import { useJobsIndexQuery } from 'daiquiri/query/assets/js/hooks/queries'
import { basePath } from 'daiquiri/query/assets/js/utils/location'

import Loading from 'daiquiri/core/assets/js/components/Loading'

const Jobs = ({ jobId, loadJob, loadJobs }) => {
  const { data: jobs } = useJobsIndexQuery()

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

  return (
    <div className="query-jobs card card-nav mb-3">
      <div className="card-header">
        {gettext('Job list')}
      </div>
      {
        isNil(jobs) ? (
          <div className="card-body">
            <Loading />
          </div>
        ) : (
          isEmpty(jobs) ? (
            <div className="card-body">
              {gettext('No jobs found.')}
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
                              {
                                openRunIds.includes(runId) ? (
                                  <i className="bi bi-folder2-open ms-auto"></i>
                                ) : (
                                  <i className="bi bi-folder ms-auto"></i>
                                )
                              }
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
                                {
                                  jobPhaseSpinner.includes(job.phase) ? (
                                    <div className="spinner-border spinner-border-sm"></div>
                                  ) : (
                                    <i className={jobPhaseIcons[job.phase]}></i>
                                  )
                                }
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
        )
      }
      {
        userId && (
          <div className="card-footer">
            <button className="btn btn-link" onClick={loadJobs}>
              {gettext('View verbose job list')}
            </button>
          </div>
        )
      }
    </div>
  )
}

Jobs.propTypes = {
  jobId: PropTypes.string,
  loadJob: PropTypes.func.isRequired,
  loadJobs: PropTypes.func.isRequired
}

export default Jobs
