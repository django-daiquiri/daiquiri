import React from 'react'
import PropTypes from 'prop-types'

import { useModal } from 'daiquiri/core/assets/js/hooks/modal'

import Query from 'daiquiri/core/assets/js/components/Query'

import RenameModal from 'daiquiri/query/assets/js/components/modals/RenameModal'
import AbortModal from 'daiquiri/query/assets/js/components/modals/AbortModal'
import ArchiveModal from 'daiquiri/query/assets/js/components/modals/ArchiveModal'

import JobParameters from './JobParameters'

const JobOverview = ({ job, loadForm }) => {
  const renameModal = useModal()
  const abortModal = useModal()
  const archiveModal = useModal()

  return (
    <div className="job-overview">
      <p>
        {gettext(
          'On this page, you can find an overview about a submitted query job.' +
            ' For a table view of the results, the plotting tool, and to access' +
            ' the download form, please use the tabs at the top of the page.'
        )}
      </p>

      {job.query && (
        <div className="card mb-3">
          <div className="card-header">
            <div className="d-flex align-items-center">
              {gettext('Query')}
              <span className="badge text-bg-secondary ms-auto">
                {job.query_language_label}
              </span>
            </div>
          </div>
          <div className="card-body">
            <Query query={job.query} />
          </div>
          <div className="card-footer">
            <button
              className="btn btn-link"
              onClick={() => loadForm('sql', job.query, job.query_language)}
            >
              {gettext('Open new query form with this query')}
            </button>
          </div>
        </div>
      )}

      <div className="card mb-3">
        <div className="card-header">{gettext('Job parameters')}</div>
        <div className="card-body">
          <JobParameters job={job} />
        </div>
        <div className="card-footer">
          {job.phase == 'COMPLETED' && (
            <button className="btn btn-link d-block" onClick={renameModal.show}>
              {gettext("Rename the job's result table or run id")}
            </button>
          )}
          {['EXECUTING', 'PENDING', 'QUEUED'].includes(job.phase) ? (
            <button className="btn btn-link d-block" onClick={abortModal.show}>
              {gettext('Abort the job')}
            </button>
          ) : (
            <button
              className="btn btn-link d-block"
              onClick={archiveModal.show}
            >
              <i className="bi bi-archive me-1"></i>
              {gettext('Archive the job')}
            </button>
          )}
        </div>
      </div>

      {job.native_query && (
        <div className="card mb-3">
          <div className="card-header">{gettext('Native query')}</div>
          <div className="card-body">
            <Query query={job.native_query} />
          </div>
        </div>
      )}

      {job.actual_query && (
        <div className="card mb-3">
          <div className="card-header">{gettext('Actual query')}</div>
          <div className="card-body">
            <Query query={job.actual_query} />
          </div>
        </div>
      )}

      <RenameModal modal={renameModal} job={job} />
      <AbortModal modal={abortModal} job={job} />
      <ArchiveModal modal={archiveModal} job={job} />
    </div>
  )
}

JobOverview.propTypes = {
  job: PropTypes.object.isRequired,
  loadForm: PropTypes.func.isRequired,
}

export default JobOverview
