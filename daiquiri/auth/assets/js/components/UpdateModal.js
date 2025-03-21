import React from 'react'
import PropTypes from 'prop-types'
import { get, isEmpty } from 'lodash'

import Checkbox from 'daiquiri/core/assets/js/components/form/Checkbox'
import Input from 'daiquiri/core/assets/js/components/form/Input'
import Select from 'daiquiri/core/assets/js/components/form/Select'

const UpdateModal = ({ modal, values, errors, details, groups, setValues, onSubmit }) => {
  return (
    <div ref={modal.ref} className="modal" tabIndex="-1">
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{gettext('Update user')}</h5>
            <button type="button" className="btn-close" onClick={modal.hide}></button>
          </div>
          {
            values.id && (
              <div className="modal-body">
                <form onSubmit={() => onSubmit(modal)}>
                  <div className="row">
                    <div className="col-md-6">
                      <Input
                        label={gettext('First name')}
                        value={values.user.first_name}
                        errors={errors.first_name}
                        onChange={value => setValues({...values, user: {...values.user, first_name: value}})}
                      />
                    </div>
                    <div className="col-md-6">
                      <Input
                        label={gettext('Last name')}
                        value={values.user.last_name}
                        errors={errors.last_name}
                        onChange={value => setValues({...values, user: {...values.user, last_name: value}})}
                      />
                    </div>
                  </div>
                  <div>
                    <Input
                      label={gettext('Email')}
                      value={values.user.email}
                      errors={errors.email}
                      onChange={value => setValues({...values, user: {...values.user, email: value}})}
                    />
                  </div>
                  {
                    !isEmpty(details) && (
                      <>
                        <div className="modal-separator"></div>
                        <div className="row">
                          {
                            details.map((detail, detailIndex) => (
                              <div key={detailIndex} className="col-md-6">
                                {
                                  detail.data_type == 'select' ? (
                                    <Select
                                      label={detail.label}
                                      value={get(values, `details.${detail.key}`, '')}
                                      errors={errors[detail.key]}
                                      options={detail.options}
                                      onChange={value => setValues({
                                        ...values, details: {...values.details, [detail.key]: value}
                                      })}
                                    />
                                  ) : (
                                    <Input
                                      label={detail.label}
                                      value={get(values, `details.${detail.key}`, '')}
                                      errors={errors[detail.key]}
                                      onChange={value => setValues({
                                        ...values, details: {...values.details, [detail.key]: value}
                                      })}
                                    />
                                  )
                                }
                              </div>
                            ))
                          }
                        </div>
                      </>
                    )
                  }
                  {
                    !isEmpty(groups) && (
                      <>
                        <div className="modal-separator"></div>
                        <strong className="d-block mb-2">{gettext('Groups')}</strong>
                        {
                          groups.map((group, groupIndex) => (
                            <Checkbox
                              key={groupIndex}
                              label={group.name}
                              checked={values.user.groups.includes(group.id)}
                              onChange={value => setValues({
                                ...values, user: { ...values.user, groups: value ? (
                                    [...values.user.groups, group.id]
                                  ) : (
                                    values.user.groups.filter(g => g != group.id)
                                  )
                                }
                              })}
                            />
                          ))
                        }
                      </>
                    )
                  }
                </form>
              </div>
            )
          }
          <div className="modal-footer">
            <button type="button" className="btn btn-sm btn-secondary" onClick={modal.hide}>
              {gettext('Close')}
            </button>
            <button type="button" className="btn btn-sm btn-primary" onClick={() => onSubmit(modal)}>
              {gettext('Update user')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

UpdateModal.propTypes = {
  modal: PropTypes.object.isRequired,
  values: PropTypes.object.isRequired,
  errors: PropTypes.object.isRequired,
  details: PropTypes.array,
  groups: PropTypes.array,
  setValues: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired
}

export default UpdateModal
