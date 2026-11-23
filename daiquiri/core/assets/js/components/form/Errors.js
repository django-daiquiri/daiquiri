import React from 'react'
import PropTypes from 'prop-types'
import { isEmpty } from 'lodash'

const Errors = ({ errors }) => {
  const messages = Array.isArray(errors) ? errors : typeof errors === 'string' ? [errors] : []

  return !isEmpty(messages) && (
    <ul className="list-unstyled invalid-feedback">
      {
        messages.map((error, index) => <li key={index}>{error}</li>)
      }
    </ul>
  )
}

Errors.propTypes = {
  errors: PropTypes.oneOfType([PropTypes.array, PropTypes.string])
}

export default Errors
