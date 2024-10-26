import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Tooltip from 'daiquiri/core/assets/js/components/Tooltip'

const Functions = ({ functions, activeItem, setActiveItem, getTooltip, onDoubleClick }) => {
  const handleClick = (item) => {
    if (item != activeItem) {
      setActiveItem({ type: 'function', ...item })
    }
  }

  return (
    <div className="mb-4">
      <div className="card">
        <div className="dq-browser">
          <div className="dq-browser-title">
            {gettext('Functions')}
          </div>
          <ul className="dq-browser-list">
            {
              functions && functions.map((func) => (
                <li key={func.id}>
                  <Tooltip tooltip={getTooltip(func)}>
                    <button
                      className={classNames('btn btn-link d-flex', {'active': activeItem === func})}
                      onClick={() => handleClick(func)}
                      onDoubleClick={() => onDoubleClick('function', func)}
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
    </div>
  )
}

Functions.defaultProps = {
  getTooltip: () => {},
  onDoubleClick: () => {}
}

Functions.propTypes = {
  functions: PropTypes.array,
  activeItem: PropTypes.object,
  setActiveItem: PropTypes.func,
  getTooltip: PropTypes.func,
  onDoubleClick: PropTypes.func
}

export default Functions
