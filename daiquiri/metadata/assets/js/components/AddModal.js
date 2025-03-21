import React from 'react'
import PropTypes from 'prop-types'

import Input from 'daiquiri/core/assets/js/components/form/Input'
import Select from 'daiquiri/core/assets/js/components/form/Select'

const AddModal = ({ modal, values, errors, schemas, tables, setValues, onSubmit }) => {
  return (
    <div ref={modal.ref} className="modal" id="add-metadata-modal" tabIndex="-1">
      <div className="modal-dialog">
        {
          values && (
            <div className="modal-content">
              <div className="modal-header">
                Add {values.type}
              </div>
              <div className="modal-body">
                {
                  (values.type == 'table') && (
                    <Select
                      label={gettext('Schema')}
                      value={values.schema}
                      options={schemas}
                      errors={errors.name}
                      onChange={(schema) => setValues({ ...values, schema })}
                    />
                  )
                }
                {
                  values.type == 'column' && (
                    <Select
                      label={gettext('Table')}
                      value={values.table}
                      options={tables}
                      errors={errors.table}
                      onChange={(table) => setValues({ ...values, table })}
                    />
                  )
                }
                <Input
                  label={gettext('Name')}
                  value={values.name || ''}
                  errors={errors.name}
                  onChange={(name) => setValues({ ...values, name })} />
                {
                  values.type == 'function' && (
                    <Input
                      label={gettext('Query string')}
                      value={values.query_string}
                      errors={errors.query_string}
                      onChange={(query_string) => setValues({ ...values, query_string })} />
                  )
                }
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-sm btn-secondary" onClick={modal.hide}>
                  {gettext('Close')}
                </button>
                <button type="button" className="btn btn-sm btn-primary" onClick={onSubmit}>
                  {gettext('Add')}
                </button>
              </div>
            </div>
          )
        }
      </div>
    </div>
  )
}

AddModal.propTypes = {
  modal: PropTypes.object,
  values: PropTypes.object,
  errors: PropTypes.object,
  schemas: PropTypes.array,
  tables: PropTypes.array,
  setValues: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired
}

export default AddModal
