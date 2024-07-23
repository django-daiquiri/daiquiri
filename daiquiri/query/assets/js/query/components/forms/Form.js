import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { useFormQuery, useQueuesQuery } from '../../hooks/queries'

import Template from 'daiquiri/core/assets/js/components/Template'

import Input from './common/Input'
import Select from './common/Select'

const Form = ({ formKey, loadJob }) => {
  const { data: form } = useFormQuery(formKey)
  const { data: queues } = useQueuesQuery()

  const [values, setValues] = useState({
    table_name: '',
    run_id: '',
    queue: '',
  })
  const [errors, setErrors] = useState({})

  const getDefaultQueue = () => isNil(queues) ? '' : queues[0].id
  const getInitialValues = () => (
    isNil(form) ? {} : {
      ...form.fields.reduce((initialValues, field) => (
        {...initialValues, [field.key]: field.default_value || ''}
      ), {})
    }
  )

  useEffect(() => {
    setValues({
      ...values,
      queue: values.queue || getDefaultQueue(),
      ...getInitialValues()
    })
  }, [form, queues])

  const handleSubmit = () => {
    console.log('handleSubmit', values)
  }

  const handleClear = () => {
    setValues({
      table_name: '',
      run_id: '',
      queue: getDefaultQueue(),
      ...getInitialValues()
    })
  }

  return form && (
    <div className="query-form mb-4">
      <h2>{form.label}</h2>
      <Template template={form.template} />

      <div className="mt-3">
        <div className="row">
        {
          form.fields.map((field, index) => (
            <div key={index} className={field.width ? `col-md-${field.width}` : 'col-md-12'}>
              <Input
                label={field.label}
                type={field.type || 'text'}
                help={field.help}
                value={values[field.key] || ''}
                errors={errors[field.key]}
                setValue={(value) => setValues({...values, [field.key]: value})}
              />
            </div>
          ))
        }
        </div>

        <div className="row">
          <div className="col-md-6">
            <Input
              label={gettext('Table name')}
              value={values.table_name}
              errors={errors.table_name}
              setValue={(table_name) => setValues({...values, table_name})}
            />
          </div>
          <div className="col-md-3">
            <Input
              label={gettext('Run id')}
              value={values.run_id}
              errors={errors.run_id}
              setValue={(run_id) => setValues({...values, run_id})}
            />
          </div>
          <div className="col-md-3">
            <Select
              label={gettext('Queue')}
              value={values.queue}
              errors={errors.queue}
              options={queues}
              setValue={(queue) => setValues({...values, queue})}
            />
          </div>
        </div>

        <div className="d-flex mt-2">
          <button type="button" className="btn btn-primary me-auto" onClick={() => handleSubmit()}>
            {form.submit}
          </button>
          <button type="button" className="btn btn-outline-secondary" onClick={() => handleClear()}>
            {gettext('Clear input window')}
          </button>
        </div>
      </div>
    </div>
  )
}

Form.propTypes = {
  formKey: PropTypes.string.isRequired,
  loadJob: PropTypes.func.isRequired,
  query: PropTypes.string
}

export default Form
