import React from 'react'
import PropTypes from 'prop-types'

import CodeMirrorDisplay from '../../../../../core/assets/js/components/CodeMirrorDisplay'
import { useToggle } from '../../../../../core/assets/js/hooks'

import JobRenameModal from './JobRenameModal'
import JobAbortModal from './JobAbortModal'
import JobArchiveModal from './JobArchiveModal'

const JobOverview = ({ job }) => {

  const [showRenameModal, toggleRenameModal] = useToggle()
  const [showAbortModal, toggleAbortModal] = useToggle()
  const [showArchiveModal, toggleArchiveModal] = useToggle()

  return (
    <div className="job-overview">
      <p>
        {gettext('On this page, you can find an overview about a submitted query job.' +
                 ' For a table view of the results, the plotting tool, and to access' +
                 ' the download form, please use the tabs at the top of the page.')}
      </p>

      <div className="card mb-3">
        <div className="card-header">
          {gettext('Query')}
        </div>
        <div className="card-body">
          <CodeMirrorDisplay value={job.query} />
        </div>
        <div className="card-footer">
          <button className="btn btn-link">
            {gettext('Open new query form with this query')}
          </button>
        </div>
      </div>

      <div className="card mb-3">
        <div className="card-header">
          {gettext('Job parameters')}
        </div>
        <div className="card-body">
          <dl className="row mb-0">
            <dt className="col-sm-4 text-end">{gettext('Job status')}</dt>
            <dd className="col-sm-8 mb-0">{job.phase}</dd>

            <dt className="col-sm-4 text-end">{gettext('Full database table name')}</dt>
            <dd className="col-sm-8 mb-0"><code>{job.schema_name}.{job.table_name}</code></dd>

            <dt className="col-sm-4 text-end">{gettext('Internal job id')}</dt>
            <dd className="col-sm-8 mb-0"><code>{job.id}</code></dd>

            <dt className="col-sm-4 text-end">{gettext('Time submitted')}</dt>
            <dd className="col-sm-8 mb-0">{job.creation_time}</dd>

            {
              job.queue && (
                <>
                  <dt className="col-sm-4 text-end">{gettext('Queue')}</dt>
                  <dd className="col-sm-8 mb-0">{job.queue}</dd>
                </>
              )
            }

            {
              job.start_time && job.creation_time && (
                <>
                  <dt className="col-sm-4 text-end">{gettext('Time in queue')}</dt>
                  <dd className="col-sm-8 mb-0">{job.time_queue} s</dd>
                </>
              )
            }

            {
              job.end_time && job.start_time && (
                <>
                  <dt className="col-sm-4 text-end">{gettext('Time for query')}</dt>
                  <dd className="col-sm-8 mb-0">{job.time_query} s</dd>
                </>
              )
            }

            {
              job.nrows !== null && (
                <>
                  <dt className="col-sm-4 text-end">{gettext('Number of rows')}</dt>
                  <dd className="col-sm-8 mb-0">{job.nrows}</dd>
                </>
              )
            }

            {
              job.size !== null && (
                <>
                  <dt className="col-sm-4 text-end">{gettext('Size of the table')}</dt>
                  <dd className="col-sm-8 mb-0">{job.size}</dd>
                </>
              )
            }

            {
              job.sources && job.sources.length && (
                <>
                  <dt className="col-sm-4 text-end">{gettext('Source tables')}</dt>
                  <dd className="col-sm-8 mb-0">
                  {
                    job.sources.map((source, sourceIndex) => (
                      <a key={sourceIndex} className="d-inline-block" href={source.url} target="blank">
                        {source.schema_name}.{source.table_name}
                      </a>
                    ))
                  }
                  </dd>
                </>
              )
            }
          </dl>
        </div>
        <div className="card-footer">
          {
            job.phase == 'COMPLETED' && (
              <button className="btn btn-link d-block" onClick={toggleRenameModal}>
                {gettext('Rename the job\'s result table or run id')}
              </button>
            )
          }
          {
            ['EXECUTING', 'PENDING', 'QUEUED'].includes(job.phase) ? (
              <button className="btn btn-link d-block" onClick={toggleAbortModal}>
                {gettext('Abort the job')}
              </button>
            ) : (
              <button className="btn btn-link d-block" onClick={toggleArchiveModal}>
                {gettext('Archive the job')}
              </button>
            )
          }
        </div>
      </div>

      <div className="card mb-3">
        <div className="card-header">
          {gettext('Native query')}
        </div>
        <div className="card-body">
          <CodeMirrorDisplay value={job.native_query} />
        </div>
      </div>

      <div className="card mb-3">
        <div className="card-header">
          {gettext('Actual query')}
        </div>
        <div className="card-body">
          <CodeMirrorDisplay value={job.actual_query} />
        </div>
      </div>

      <JobRenameModal job={job} show={showRenameModal} toggle={toggleRenameModal} />
      <JobAbortModal job={job} show={showAbortModal} toggle={toggleAbortModal} />
      <JobArchiveModal job={job} show={showArchiveModal} toggle={toggleArchiveModal} />

    </div>
  )
}

JobOverview.propTypes = {
  job: PropTypes.object.isRequired
}

export default JobOverview
