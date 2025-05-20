import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { uniqueId } from 'lodash'

import Errors from './Errors'

const SubSelect = ({
  label,
  value,
  width,
  placeholder,
  placeholder_subselect,
  options = [],
  errors,
  onChange,
}) => {
  const mainId = uniqueId('select-main-')
  const subId = uniqueId('select-sub-')
  const [mainValue, setMainValue] = useState('')
  const [subValue, setSubValue] = useState('')

  useEffect(() => {
    // If we already have a mainValue and the new value is a suboption,
    // don't change the mainValue
    if (
      mainValue &&
      options.some(
        (opt) =>
          opt.id === mainValue &&
          opt.suboptions?.some(
            (sub) => sub.id === value && sub.main_id === mainValue
          )
      )
    ) {
      setSubValue(value)
      return
    }

    // Find the main option that contains the current value
    const mainOption = options.find(
      (opt) =>
        opt.id === value ||
        opt.suboptions?.some(
          (sub) => sub.id === value && sub.main_id === opt.id
        )
    )

    if (mainOption) {
      setMainValue(mainOption.id)
    } else {
      setMainValue('')
    }
    setSubValue('')
  }, [value, options])

  const handleMainSelect = (event) => {
    const newMainValue = event.target.value
    setMainValue(newMainValue)
    setSubValue('')
    // Always call onChange with the main option value
    onChange(newMainValue)
  }

  const handleSubSelect = (event) => {
    const newSubValue = event.target.value
    setSubValue(newSubValue)

    // Find the selected suboption to verify its main_id
    const selectedSubOption = currentMainOption?.suboptions?.find(
      (sub) => sub.id === newSubValue && sub.main_id === mainValue
    )

    if (selectedSubOption) {
      onChange(newSubValue)
    }
  }

  const currentMainOption = options.find((opt) => opt.id === mainValue)

  return (
    <div className="mb-3">
      <label className="form-label">{label}</label>
      <div className="d-flex gap-2">
        {/* Main Select */}
        <div className="flex-grow-1">
          <select
            id={mainId}
            className={classNames('form-control', { 'is-invalid': errors })}
            value={mainValue}
            onChange={handleMainSelect}
            aria-describedby={errors ? `${mainId}-errors` : undefined}
          >
            <option value="">{placeholder || 'Select an option'}</option>
            {options.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label || option.text}
              </option>
            ))}
          </select>
        </div>

        {/* Sub Select - Only show if main option has suboptions */}
        {currentMainOption?.suboptions?.length > 0 && (
          <div className={width ? `col-md-${width}` : 'col-md-4'}>
            <select
              id={subId}
              className="form-control"
              value={subValue}
              onChange={handleSubSelect}
            >
              <option value="">
                {placeholder_subselect || 'Select a sub-option'}
              </option>
              {currentMainOption.suboptions
                .filter((sub) => sub.main_id === currentMainOption.id)
                .map((suboption) => (
                  <option key={suboption.id} value={suboption.id}>
                    {suboption.label || suboption.text}
                  </option>
                ))}
            </select>
          </div>
        )}
      </div>
      <Errors errors={errors} id={`${mainId}-errors`} />
    </div>
  )
}

SubSelect.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  width: PropTypes.number,
  placeholder: PropTypes.string,
  placeholder_subselect: PropTypes.string,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
      label: PropTypes.string,
      text: PropTypes.string,
      suboptions: PropTypes.arrayOf(
        PropTypes.shape({
          id: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
            .isRequired,
          main_id: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
            .isRequired,
          label: PropTypes.string,
          text: PropTypes.string,
        })
      ),
    })
  ),
  errors: PropTypes.array,
  onChange: PropTypes.func.isRequired,
}

export default SubSelect
