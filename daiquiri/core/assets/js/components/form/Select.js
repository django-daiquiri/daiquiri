import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { uniqueId } from 'lodash'

import Errors from './Errors'

const Select = ({ label, value, options, disabled, errors, onChange }) => {
  const id = uniqueId('select-')

  return (
    <div className="mb-3">
      <label htmlFor={id} className="form-label">
        {label}
      </label>
      <select
        id={id}
        key={id}
        className={classNames('form-control', { 'is-invalid': errors })}
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      >
        {options &&
          options.map((option) => (
            <option key={option.id} value={option.id}>
              {option.label || option.text}
            </option>
          ))}
      </select>
      <Errors errors={errors} />
    </div>
  )
}

Select.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
  options: PropTypes.array,
  disabled: PropTypes.bool,
  errors: PropTypes.array,
  onChange: PropTypes.func.isRequired,
}

export default Select
