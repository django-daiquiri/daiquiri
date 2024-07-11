import React from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { useFormQuery } from '../../hooks/query'

import FormSql from './FormSql'
import FormCustom from './FormCustom'
import FormUpload from './FormUpload'

const Form = ({ formKey, loadJob, query }) => {
  const { data: form } = useFormQuery(formKey)

  if (isNil(form)) {
    return null
  }

  switch (form.key) {
    case 'sql':
      return <FormSql form={form} loadJob={loadJob} query={query} />
    case 'upload':
      return <FormUpload form={form} loadJob={loadJob} />
    default:
      return <FormCustom form={form} loadJob={loadJob} />
  }
}

Form.propTypes = {
  formKey: PropTypes.string.isRequired,
  loadJob: PropTypes.func.isRequired,
  query: PropTypes.string
}

export default Form
