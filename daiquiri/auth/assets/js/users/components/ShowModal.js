import React from 'react'
import PropTypes from 'prop-types'
import { isEmpty } from 'lodash'

const ShowModal = ({ modal, values, details }) => {
  return (
    <div ref={modal.ref} className="modal" tabIndex="-1">
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{values.id && values.full_name}</h5>
            <button type="button" className="btn-close" onClick={modal.hide}></button>
          </div>
          {
            values.id && (
              <div className="modal-body">
                <div className="row">
                  <div className="col-md-6">
                    <dl className="mb-3">
                        <dt>{gettext('Username')}</dt>
                        <dd>{values.user.username}</dd>
                    </dl>
                  </div>
                  <div className="col-md-6">
                    <dl className="mb-3">
                        <dt>{gettext('Email')}</dt>
                        <dd>{values.user.email}</dd>
                    </dl>
                  </div>
                </div>
                <div className="modal-seperator"></div>
                <div className="row">
                  <div className="col-md-6">
                    <dl className="mb-3">
                        <dt>{gettext('First name')}</dt>
                        <dd>{values.user.first_name}</dd>
                    </dl>
                  </div>
                  <div className="col-md-6">
                    <dl className="mb-3">
                        <dt>{gettext('Last name')}</dt>
                        <dd>{values.user.last_name}</dd>
                    </dl>
                  </div>
                </div>
                {
                  !isEmpty(details) && !isEmpty(values.details) && (
                    <>
                      <div className="modal-seperator"></div>
                      <div className="row">
                        {
                          details.map((detail, detailIndex) => (
                            <div key={detailIndex} className="col-md-6">
                              <dl className="mb-3">
                                  <dt>{detail.label}</dt>
                                  <dd>
                                    {
                                      detail.data_type == 'select' ? (
                                        (detail.options.find(d => d.id == values.details[detail.key]) || {}).label
                                      ) : (
                                        values.details[detail.key]
                                      )
                                    }
                                  </dd>
                              </dl>
                            </div>
                          ))
                        }
                      </div>
                    </>
                  )
                }
                <div className="modal-seperator"></div>
                <dl>
                    <dt>{gettext('Date joined')}</dt>
                    <dd>{values.user.date_joined}</dd>
                </dl>
                <dl>
                    <dt>{gettext('Last login')}</dt>
                    <dd>{values.user.last_login}</dd>
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

ShowModal.propTypes = {
  modal: PropTypes.object.isRequired,
  values: PropTypes.object.isRequired,
  details: PropTypes.array,
}

export default ShowModal
