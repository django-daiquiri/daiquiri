import React from 'react'
import PropTypes from 'prop-types'
import { isEmpty } from 'lodash'

const ShowModal = ({ modal, profile, details }) => {
  return (
    <div ref={modal.ref} className="modal" tabIndex="-1">
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{profile.id && profile.full_name}</h5>
            <button type="button" className="btn-close" onClick={modal.hide}></button>
          </div>
          {
            profile.id && (
              <div className="modal-body">
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <dl>
                        <dt>{gettext('Username')}</dt>
                        <dd>{profile.user.username}</dd>
                    </dl>
                  </div>
                  <div className="col-md-6 mb-3">
                    <dl>
                        <dt>{gettext('Email')}</dt>
                        <dd>{profile.user.email}</dd>
                    </dl>
                  </div>
                  <div className="col-md-6 mb-3">
                    <dl>
                        <dt>{gettext('First name')}</dt>
                        <dd>{profile.user.first_name}</dd>
                    </dl>
                  </div>
                  <div className="col-md-6 mb-3">
                    <dl>
                        <dt>{gettext('Last name')}</dt>
                        <dd>{profile.user.last_name}</dd>
                    </dl>
                  </div>
                </div>
                {
                  !isEmpty(details) && !isEmpty(profile.details) && (
                    <>
                      <div className="modal-separator"></div>
                      <div className="row">
                        {
                          details.map((detail, detailIndex) => (
                            <div key={detailIndex} className="col-md-6 mb-3">
                              <dl>
                                  <dt>{detail.label}</dt>
                                  <dd>
                                    {
                                      detail.data_type == 'select' ? (
                                        (detail.options.find(d => d.id == profile.details[detail.key]) || {}).label
                                      ) : (
                                        profile.details[detail.key]
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
                <div className="modal-separator"></div>
                <div className="row">
                  <div className="col-md-6 mb-3 mb-md-0">
                    <dl>
                      <dt>{gettext('Date joined')}</dt>
                      <dd>{profile.user.date_joined}</dd>
                    </dl>
                  </div>
                  <div className="col-md-6">
                    <dl>
                      <dt>{gettext('Last login')}</dt>
                      <dd>{profile.user.last_login}</dd>
                    </dl>
                  </div>
                </div>
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
  profile: PropTypes.object.isRequired,
  details: PropTypes.array,
}

export default ShowModal
