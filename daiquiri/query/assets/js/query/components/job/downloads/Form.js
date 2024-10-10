import React, { useState } from 'react'
import PropTypes from 'prop-types'

import Input from '../../forms/common/Input'
import Select from '../../forms/common/Select'

const Form = ({ form, onSubmit }) => {
  const initialValues = Object.fromEntries(
    form.fields.filter(field => field.type != 'submit').map(field => [field.key, field.default_value || ''])
  )

  const [values, setValues] = useState(initialValues)

  return (
    <div className="card mb-4">
      <div className="card-header">
        {form.label}
      </div>
      <div className="card-body">
        <div className="row">
        {
          form.fields.map((field, index) => (
            <div key={index} className={field.width ? `col-md-${field.width}` : 'col-md-12'}>
              {
                ['text', 'number'].includes(field.type) && (
                  <Input
                    type={field.type}
                    label={field.label}
                    help={field.help}
                    value={values[field.key]}
                    setValue={(value) => setValues({...values, [field.key]: value})}
                  />
                )
              }
              {
                field.type == 'select' && (
                  <Select
                    label={field.label}
                    help={field.help}
                    value={values[field.key]}
                    options={field.options}
                    setValue={(value) => setValues({...values, [field.key]: value})} />
                )
              }
              {
                field.type == 'submit' && (
                  <div>
                    <label className="form-label">&nbsp;</label>
                    <button type="button" className="btn btn-primary form-control" onClick={() => onSubmit(values)}>
                      {field.label || gettext('Submit')}
                    </button>
                  </div>
                )
              }
            </div>
          ))
        }
        </div>
      </div>
    </div>
  )
}

Form.propTypes = {
  form: PropTypes.object.isRequired,
  onSubmit: PropTypes.func.isRequired
}

export default Form
