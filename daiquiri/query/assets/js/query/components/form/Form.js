import React from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { useFormQuery } from '../../hooks/query'

import FormSql from './FormSql'
import FormCustom from './FormCustom'
import FormUpload from './FormUpload'

const Form = ({ formKey }) => {
  const { data: form } = useFormQuery(formKey)

  if (isNil(form)) {
    return null
  }

  switch (form.key) {
    case 'sql':
      return <FormSql form={form} />
    case 'upload':
      return <FormUpload form={form} />
    default:
      return <FormCustom form={form} />
  }
}

Form.propTypes = {
  formKey: PropTypes.string.isRequired
}

export default Form
