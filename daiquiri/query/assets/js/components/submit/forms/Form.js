import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isEmpty, isNil } from 'lodash'

import {
  useFormQuery,
  useQueuesQuery,
} from 'daiquiri/query/assets/js/hooks/queries'
import { useSubmitJobMutation } from 'daiquiri/query/assets/js/hooks/mutations'

import Template from 'daiquiri/core/assets/js/components/Template'

import Errors from 'daiquiri/core/assets/js/components/form/Errors'
import Input from 'daiquiri/core/assets/js/components/form/Input'
import Select from 'daiquiri/core/assets/js/components/form/Select'
import SubSelect from 'daiquiri/core/assets/js/components/form/SubSelect'

const Form = ({ formKey, loadJob }) => {
  const { data: form } = useFormQuery(formKey)
  const { data: queues } = useQueuesQuery()
  const mutation = useSubmitJobMutation()

  const [values, setValues] = useState({
    table_name: '',
    run_id: '',
    queue: '',
  })
  const [errors, setErrors] = useState({})

  const getDefaultQueue = () => (isNil(queues) ? '' : queues[0].id)
  const getInitialValues = () =>
    isNil(form) || isEmpty(form.fields)
      ? {}
      : {
          ...form.fields.reduce(
            (initialValues, field) => ({
              ...initialValues,
              [field.key]: field.default_value || '',
            }),
            {}
          ),
        }

  const handleSubmit = () => {
    mutation.mutate({ values, setErrors, loadJob, formKey })
  }

  const handleClear = () => {
    setValues({
      table_name: '',
      run_id: '',
      queue: getDefaultQueue(),
      ...getInitialValues(),
    })
  }

  useEffect(() => {
    setValues({
      ...values,
      queue: values.queue || getDefaultQueue(),
      ...getInitialValues(),
    })
  }, [form, queues])

  if (isNil(form)) {
    return null
  } else if (form.errors) {
    return (
      <p className="text-danger">
        {gettext(
          'An error occurred while retrieving the form from the server:'
        )}{' '}
        {form.errors.api
          ? form.errors.api.join(', ')
          : gettext('No error message provided.')}
      </p>
    )
  } else {
    return (
      <div className="query-form mb-4">
        <h2>{form.label}</h2>
        <Template template={form.template} />
        <div className="mt-3">
          <div className="form-group row mb-2">
            {form.fields &&
              form.fields.map((field, index) => (
                <div
                  key={index}
                  className={
                    field.width ? `col-md-${field.width}` : 'col-md-12'
                  }
                >
                  {['text', 'number'].includes(field.type) && (
                    <Input
                      label={field.label}
                      type={field.type}
                      help={field.help}
                      value={values[field.key] || field.default_value}
                      errors={errors[field.key]}
                      onChange={(value) =>
                        setValues({ ...values, [field.key]: value })
                      }
                    />
                  )}
                  {field.type == 'select' && (
                    <Select
                      label={field.label}
                      help={field.help}
                      value={values[field.key] || field.default_value}
                      options={field.options}
                      errors={errors[field.key]}
                      onChange={(value) =>
                        setValues({ ...values, [field.key]: value })
                      }
                    />
                  )}
                  {field.type == 'subselect' && (
                    <SubSelect
                      label={field.label}
                      help={field.help}
                      value={values[field.key] || field.default_value}
                      options={field.options}
                      width={field.width_subselect}
                      placeholder={field.placeholder}
                      placeholder_subselect={field.placeholder_subselect}
                      errors={errors[field.key]}
                      onChange={(value) =>
                        setValues({ ...values, [field.key]: value })
                      }
                    />
                  )}
                </div>
              ))}
          </div>

          <div className="row">
            <div className="col-md-6">
              <Input
                label={gettext('Table name')}
                value={values.table_name}
                errors={errors.table_name}
                onChange={(table_name) => setValues({ ...values, table_name })}
              />
            </div>
            <div className="col-md-3">
              <Input
                label={gettext('Run id')}
                value={values.run_id}
                errors={errors.run_id}
                onChange={(run_id) => setValues({ ...values, run_id })}
              />
            </div>
            <div className="col-md-3">
              <Select
                label={gettext('Queue')}
                value={values.queue}
                errors={errors.queue}
                options={queues}
                onChange={(queue) => setValues({ ...values, queue })}
              />
            </div>
          </div>

          {errors.query && (
            <div>
              <div className="is-invalid"></div>
              <Errors errors={errors.query.messages} />
            </div>
          )}

          {errors.query_language && (
            <div>
              <div className="is-invalid"></div>
              <Errors errors={errors.query_language} />
            </div>
          )}

          <div className="d-flex mt-2">
            <button
              type="button"
              className="btn btn-primary me-auto"
              onClick={() => handleSubmit()}
            >
              {form.submit || gettext('Submit')}
            </button>
            <button
              type="button"
              className="btn btn-outline-secondary"
              onClick={() => handleClear()}
            >
              {gettext('Clear input window')}
            </button>
          </div>
        </div>
      </div>
    )
  }
}

Form.propTypes = {
  formKey: PropTypes.string.isRequired,
  loadJob: PropTypes.func.isRequired,
  query: PropTypes.string,
}

export default Form
