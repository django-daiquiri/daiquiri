import React from 'react'
import PropTypes from 'prop-types'

import Template from 'daiquiri/core/assets/js/components/Template'

const FormCustom = ({ form, loadJob }) => {
  return (
    <div className="form">
      <h2>{form.label}</h2>
      <Template template={form.template} />
    </div>
  )
}

FormCustom.propTypes = {
  form: PropTypes.object.isRequired,
  loadJob: PropTypes.func.isRequired
}

export default FormCustom
