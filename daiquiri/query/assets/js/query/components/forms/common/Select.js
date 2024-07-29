import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Errors from './Errors'

const Select = ({ label, value, options, errors, setValue }) => {
  return (
    <div className="mb-2">
      <label htmlFor="queue" className="form-label">{label}</label>
      <select
        id="queue"
        className={classNames('form-control', {'is-invalid': errors})}
        value={value}
        onChange={(event) => setValue(event.target.value)}>
      {
        options && options.map((option) => <option key={option.id} value={option.id}>{option.text}</option>)
      }
      </select>
      <Errors errors={errors} />
    </div>
  )
}

Select.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  options: PropTypes.array,
  errors: PropTypes.array,
  setValue: PropTypes.func.isRequired,
}

export default Select
