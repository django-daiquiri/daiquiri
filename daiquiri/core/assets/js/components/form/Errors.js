import React from 'react'
import PropTypes from 'prop-types'
import { isEmpty } from 'lodash'

const Errors = ({ errors }) => {
  return !isEmpty(errors) && (
    <ul className="list-unstyled invalid-feedback">
      {
        errors.map((error, index) => <li key={index}>{error}</li>)
      }
    </ul>
  )
}

Errors.propTypes = {
  errors: PropTypes.array
}

export default Errors
