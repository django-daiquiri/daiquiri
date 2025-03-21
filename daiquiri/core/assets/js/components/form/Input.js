import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { uniqueId } from 'lodash'

import Errors from './Errors'

const Input = ({ label, type, help, value, disabled, errors, onChange }) => {
  const id = uniqueId('input-')

  return (
    <div className="mb-3">
      <label htmlFor={id} className="form-label">{label}</label>
      <input
        id={id}
        type={type}
        className={classNames('form-control', {'is-invalid': errors})}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}></input>
      <Errors errors={errors} />
      {
        help && <div className="form-text">{help}</div>
      }
    </div>
  )
}

Input.defaultProps = {
  type: 'text'
}

Input.propTypes = {
  label: PropTypes.string.isRequired,
  type: PropTypes.string,
  help: PropTypes.string,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number
  ]).isRequired,
  disabled: PropTypes.bool,
  errors: PropTypes.array,
  onChange: PropTypes.func,
}

export default Input
