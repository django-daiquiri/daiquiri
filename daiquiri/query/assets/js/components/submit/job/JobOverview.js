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

      <div className="card mb-3">
        <div className="card-header">
          <div className="d-flex align-items-center">
            {gettext('Job actions')}
          </div>
        </div>
        <div className="card-body d-flex flex-wrap gap-2">
            <button
              className="btn btn-outline-primary btn-sm"
              onClick={() => loadForm('sql', job.query, job.query_language)}
            >
              <i className="bi bi-arrow-repeat me-2"></i>
              {gettext('Reuse query')}
            </button>
            {job.phase == 'COMPLETED' && (
              <button className="btn btn-outline-secondary btn-sm" onClick={renameModal.show}>
                <i className="bi bi-pencil-square me-2"></i>
                {gettext("Rename results")}
              </button>
            )}
            {['EXECUTING', 'PENDING', 'QUEUED'].includes(job.phase) ? (
              <button className="btn btn-outline-danger btn-sm ms-auth" onClick={abortModal.show}>
                <i className="bi bi-trash me-2"></i>
                {gettext('Abort the job')}
              </button>
            ) : (
              <button
                className="btn btn-outline-danger btn-sm ms-auto"
                onClick={archiveModal.show}
              >
                <i className="bi bi-trash me-2"></i>
                {gettext('Archive job')}
              </button>
            )}
        </div>
      </div>

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
        </div>
      )}

      <div className="card mb-3">
        <div className="card-header">{gettext('Job parameters')}</div>
        <div className="card-body">
          <JobParameters job={job} />
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
