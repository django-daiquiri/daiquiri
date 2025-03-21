import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { uniqueId } from 'lodash'

import Errors from './Errors'

const Textarea = ({ label, rows, help, value, errors, onChange }) => {
  const id = uniqueId('input-')

  return (
    <div className="mb-3">
      <label htmlFor={id} className="form-label">{label}</label>
      <textarea
        id={id}
        rows={rows}
        className={classNames('form-control', {'is-invalid': errors})}
        value={value}
        onChange={(event) => onChange(event.target.value)}></textarea>
      <Errors errors={errors} />
      {
        help && <div className="form-text">{help}</div>
      }
    </div>
  )
}

Textarea.defaultProps = {
  rows: 4
}

Textarea.propTypes = {
  label: PropTypes.string.isRequired,
  rows: PropTypes.number.isRequired,
  help: PropTypes.string,
  value: PropTypes.string.isRequired,
  errors: PropTypes.array,
  onChange: PropTypes.func.isRequired,
}

export default Textarea
