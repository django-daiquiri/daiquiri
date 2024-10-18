import React, { useState } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { isEmpty } from 'lodash'

import Tooltip from 'daiquiri/core/assets/js/components/Tooltip'

import { useUserFunctionsQuery } from 'daiquiri/metadata/assets/js/hooks/queries'

const FunctionsDropdown = ({ onPaste }) => {
  const { data: functions } = useUserFunctionsQuery()

  const [activeItem, setActiveItem] = useState(null)
  const [filterValue, setFilterValue] = useState('')

  const handleClick = (item) => {
    if (item != activeItem) {
      setActiveItem(item)
    }
  }

  return (
    <div className="mb-4">
      <div className="card">
        <div className="dq-browser">
          <div className="dq-browser-title">
            {gettext('Columns')}
          </div>
          <div className="dq-browser-filter">
            <input
              type="text"
              className="form-control"
              placeholder={gettext('Filter functions')}
              value={filterValue}
              onChange={(event) => setFilterValue(event.target.value)}>
            </input>
          </div>
          <ul className="dq-browser-list">
            {
              functions && functions.filter(
                (func) => (isEmpty(filterValue) || func.name.includes(filterValue))
              ).map((func) => (
                <li key={func.id}>
                  <Tooltip title={func.description} placement="left">
                    <button
                      className={classNames('btn btn-link d-flex', {'active': activeItem === func})}
                      onClick={() => handleClick(func)}
                      onDoubleClick={() => onPaste(func)}
                    >
                      <div>{func.name}</div>
                    </button>
                  </Tooltip>
                </li>
              ))
            }
          </ul>
        </div>
      </div>
      <small className="form-text text-muted">
        {gettext('A double click will paste the function into the query field.')}
      </small>
    </div>
  )
}

FunctionsDropdown.propTypes = {
  onPaste: PropTypes.func.isRequired
}

export default FunctionsDropdown
