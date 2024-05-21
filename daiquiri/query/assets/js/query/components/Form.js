import React from 'react'
import PropTypes from 'prop-types'

const Form = ({ formKey }) => {
  return (
    <div className="form">
      <h2>{formKey}</h2>
    </div>
  )
}

Form.propTypes = {
  formKey: PropTypes.string.isRequired
}

export default Form
