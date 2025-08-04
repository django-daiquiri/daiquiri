import React from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'
import classNames from 'classnames'

import { useLsState } from 'daiquiri/core/assets/js/hooks/ls'
import { useJobQuery } from 'daiquiri/query/assets/js/hooks/queries'

import JobOverview from './JobOverview'
import JobResults from './JobResults'
import JobPlot from './JobPlot'
import JobDownload from './JobDownload'

const Job = ({ jobId, loadForm, loadJob }) => {
  const { data: job } = useJobQuery(jobId)

  const [activeTab, setActiveTab] = useLsState('daiquiri.query.job.activeTab', 'overview')

  const handleClick = (event, tab) => {
    event.preventDefault()
    setActiveTab(tab)
  }

  if (isNil(job)) {
    return null
  } else if (job.errors) {
    return (
      <p className="text-danger">
        {gettext('An error occurred while retrieving the job from the server:')}
        {' '}
        {job.errors.api ? job.errors.api.join(', ') : gettext('No error message provided.')}
      </p>
    )
  } else {
    return (
      <div className="job">
        <h2 className="mb-4">
          {interpolate(gettext('Query job `%s`'), [job.table_name])}
        </h2>
        <ul className="job-tabs nav nav-tabs">
          <li className="nav-item">
            <a className={classNames('nav-link', {'active': activeTab === 'overview'})} href="#"
               onClick={(event) => handleClick(event, 'overview')}>
              {gettext('Job overview')}
            </a>
          </li>
          <li className="nav-item">
            <a className={classNames('nav-link', {'active': activeTab === 'results'})} href="#"
              onClick={(event) => handleClick(event, 'results')}>
              {gettext('Results table')}
            </a>
          </li>
          <li className="nav-item">
            <a className={classNames('nav-link', {'active': activeTab === 'plot'})} href="#"
              onClick={(event) => handleClick(event, 'plot')}>
              {gettext('Plot')}
            </a>
          </li>
          <li className="nav-item">
            <a className={classNames('nav-link', {'active': activeTab === 'download'})} href="#"
              onClick={(event) => handleClick(event, 'download')}>
              {gettext('Download')}
            </a>
          </li>
        </ul>
        <div className="job-tab-content mt-3">
          {
            activeTab === 'overview' && <JobOverview job={job} loadForm={loadForm} />
          }
          {
            activeTab === 'results' && <JobResults job={job} />
          }
          {
            activeTab === 'plot' && <JobPlot job={job} loadJob={loadJob}/>
          }
          {
            activeTab === 'download' && <JobDownload job={job} />
          }
        </div>
      </div>
    )
  }
}

Job.propTypes = {
  jobId: PropTypes.string.isRequired,
  loadForm: PropTypes.func.isRequired,
  loadJob: PropTypes.func.isRequired,
}

export default Job
