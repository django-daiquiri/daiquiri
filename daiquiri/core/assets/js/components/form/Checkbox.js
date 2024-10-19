import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { uniqueId } from 'lodash'

import Errors from './Errors'

const Checkbox = ({ label, help, checked, errors, onChange }) => {
  const id = uniqueId('input-')

  return (
    <div className="form-check">
      <input
        id={id}
        type="checkbox"
        className={classNames('form-check-input ', {'is-invalid': errors})}
        checked={checked}
        onChange={() => onChange(!checked)}
      />
      <label className="form-check-label user-select-none" htmlFor={id}>{label}</label>
      <Errors errors={errors} />
      {
        help && <div className="form-text">{help}</div>
      }
    </div>
  )
}

Checkbox.propTypes = {
  label: PropTypes.string.isRequired,
  help: PropTypes.string,
  checked: PropTypes.bool.isRequired,
  errors: PropTypes.array,
  onChange: PropTypes.func.isRequired,
}

export default Checkbox
