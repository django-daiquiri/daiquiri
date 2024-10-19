import React from 'react'
import PropTypes from 'prop-types'

const Modal = ({ modal, message }) => {
  return (
    <div ref={modal.ref} className="modal" tabIndex="-1">
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{gettext('Contact message')}</h5>
            <button type="button" className="btn-close" onClick={modal.hide}></button>
          </div>
          {
            message.id && (
              <div className="modal-body">
                <dl>
                    <dt>{gettext('Author')}</dt>
                    <dd>{message.author}</dd>
                </dl>
                <dl>
                    <dt>{gettext('Email')}</dt>
                    <dd>{message.email}</dd>
                </dl>
                <dl>
                    <dt>{gettext('Created')}</dt>
                    <dd>{message.created_label}</dd>
                </dl>
                <dl>
                    <dt>{gettext('Status')}</dt>
                    <dd>{message.status_label}</dd>
                </dl>
                <div className="modal-seperator"></div>
                <dl>
                    <dt>{gettext('Subject')}</dt>
                    <dd>{message.subject}</dd>
                </dl>
                <dl>
                    <dt>{gettext('Message')}</dt>
                    <dd>{message.message}</dd>
                </dl>
              </div>
            )
          }
          <div className="modal-footer">
            <button type="button" className="btn btn-sm btn-secondary" onClick={modal.hide}>
              {gettext('Close')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

Modal.propTypes = {
  modal: PropTypes.object.isRequired,
  message: PropTypes.object,
}

export default Modal
