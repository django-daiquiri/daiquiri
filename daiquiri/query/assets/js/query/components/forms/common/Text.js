import React from 'react'
import PropTypes from 'prop-types'
import classname from 'classnames'

import Errors from './Errors'

const Text = ({ label, value, errors, setValue }) => {
  return (
    <div className="mb-2">
      <label htmlFor="run-id" className="form-label">{label}</label>
      <input
        id="run-id"
        type="text"
        className={classname('form-control', {'is-invalid': errors})}
        value={value}
        onChange={(event) => setValue(event.target.value)}></input>
      <Errors errors={errors} />
    </div>
  )
}

Text.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  errors: PropTypes.array,
  setValue: PropTypes.func.isRequired,
}

export default Text
