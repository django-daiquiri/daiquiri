import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import className from 'classnames'

import { useUpdateJobMutation } from 'daiquiri/query/assets/js/hooks/mutations'

const RenameModal = ({ modal, job }) => {
  const [values, setValues] = useState({table_name: '', run_id: ''})
  const [errors, setErrors] = useState({})

  const mutation = useUpdateJobMutation()

  useEffect(() => {
    setValues({table_name: job.table_name, run_id: job.run_id})
    setErrors({})
  }, [job])

  const handleSubmit = () => {
    mutation.mutate({job, values, setErrors, onSuccess: modal.hide})
  }

  return (
    <div ref={modal.ref} className="modal" tabIndex="-1">
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{gettext('Update job')}</h5>
            <button type="button" className="btn-close" onClick={modal.hide}></button>
          </div>
          <div className="modal-body">
            <div className="mb-3">
              <label htmlFor="rename-model-table-name" className="form-label">
                {gettext('Table name')}
              </label>
              <input
                type="text"
                className={className('form-control', {'is-invalid': errors.table_name})}
                id="rename-model-table-name"
                value={values.table_name || ''}
                onChange={(event) => setValues({...values, table_name: event.target.value})}
              />
              <div className="invalid-feedback">
                {errors.table_name}
              </div>
            </div>
            <div className="mb-0">
              <label htmlFor="rename-model-run-id" className="form-label">
                {gettext('Run id')}
              </label>
              <input
                type="text"
                className={className('form-control', {'is-invalid': errors.run_id})}
                id="rename-model-run-id"
                value={values.run_id || ''}
                onChange={(event) => setValues({...values, run_id: event.target.value})}
              />
              <div className="invalid-feedback">
                {errors.table_name}
              </div>
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-sm btn-secondary" onClick={modal.hide}>
              {gettext('Close')}
            </button>
            <button type="button" className="btn btn-sm btn-primary" onClick={handleSubmit}>
              {gettext('Save')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

RenameModal.propTypes = {
  modal: PropTypes.object.isRequired,
  job: PropTypes.object.isRequired
}

export default RenameModal
