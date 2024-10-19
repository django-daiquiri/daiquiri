import React from 'react'
import PropTypes from 'prop-types'

const ConfirmModal = ({ modal, label, action, onSubmit }) => {
  return (
    <div ref={modal.ref} className="modal" tabIndex="-1">
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{label}</h5>
            <button type="button" className="btn-close" onClick={modal.hide}></button>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-sm btn-secondary" onClick={modal.hide}>
              {gettext('Close')}
            </button>
            <button type="button" className="btn btn-sm btn-primary" onClick={() => onSubmit(modal, action)}>
              {label}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

ConfirmModal.propTypes = {
  modal: PropTypes.object.isRequired,
  label: PropTypes.string.isRequired,
  action: PropTypes.string.isRequired,
  onSubmit: PropTypes.func.isRequired
}

export default ConfirmModal
