import React from 'react'
import PropTypes from 'prop-types'

import { useArchiveJobMutation } from 'daiquiri/query/assets/js/hooks/mutations'

const ArchiveModal = ({ modal, job }) => {
  const mutation = useArchiveJobMutation()

  const handleSubmit = () => {
    mutation.mutate({job, onSuccess: modal.hide()})
  }

  return (
    <div ref={modal.ref} className="modal" tabIndex="-1">
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{gettext('Archive job')}</h5>
            <button type="button" className="btn-close" onClick={modal.hide}></button>
          </div>
          <div className="modal-body">
            <p dangerouslySetInnerHTML={{
              __html: interpolate(gettext('You are about to archive the job <code>%s</code>.'), [job.id])
            }} />
            <p className="text-danger">
              {gettext('This action cannot be undone!')}
            </p>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-sm btn-secondary" onClick={modal.hide}>
              {gettext('Close')}
            </button>
            <button type="button" className="btn btn-sm btn-danger" onClick={handleSubmit}>
              {gettext('Archive')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

ArchiveModal.propTypes = {
  modal: PropTypes.object.isRequired,
  job: PropTypes.object.isRequired
}

export default ArchiveModal
