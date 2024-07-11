import React, { useEffect } from 'react'
import PropTypes from 'prop-types'

import { useModal } from 'daiquiri/core/assets/js/hooks/modal'

import { useAbortJobMutation } from '../../hooks/mutations'

const JobAbortModal = ({ job, show, toggle }) => {
  const [ref, showModal, hideModal]  = useModal()

  useEffect(() => {
    if (show) {
      showModal()
    }
  }, [show])

  const mutation = useAbortJobMutation()

  const handleSubmit = () => {
    mutation.mutate({job, onSuccess: handleClose})
  }

  const handleClose = () => {
    hideModal()
    toggle()
  }

  return (
    <div ref={ref} className="modal" tabIndex="-1">
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{gettext('Archive job')}</h5>
            <button type="button" className="btn-close" onClick={handleClose}></button>
          </div>
          <div className="modal-body">
            <p dangerouslySetInnerHTML={{
              __html: interpolate(gettext('You are about to abort the job <code>%s</code>.'), [job.id])
            }} />
            <p className="text-danger">
              {gettext('This action cannot be undone!')}
            </p>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-sm btn-secondary" onClick={handleClose}>
              {gettext('Close')}
            </button>
            <button type="button" className="btn btn-sm btn-danger" onClick={handleSubmit}>
              {gettext('Abort')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

JobAbortModal.propTypes = {
  job: PropTypes.object.isRequired,
  show: PropTypes.bool.isRequired,
  toggle: PropTypes.func.isRequired
}

export default JobAbortModal
