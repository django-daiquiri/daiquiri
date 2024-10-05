import React from 'react'
import PropTypes from 'prop-types'

const TableModalNavigation = ({ values, onClick }) => {
  return (
    <div className="dq-table-modal-navigation position-absolute top-0 end-0 mt-3 me-3">
      <div className="position-relative w-100 h-100">
        {
          values.up && (
            <div className="position-absolute top-0 start-50 translate-middle-x">
              <button className="btn btn-link" onClick={() => onClick('up')}>
                <span className="material-symbols-rounded">
                  keyboard_arrow_up
                </span>
              </button>
            </div>
          )
        }
        {
          values.down && (
            <div className="position-absolute bottom-0 start-50 translate-middle-x">
              <button className="btn btn-link" onClick={() => onClick('down')}>
                <span className="material-symbols-rounded">
                  keyboard_arrow_down
                </span>
              </button>
            </div>
          )
        }
        {
          values.left && (
            <div className="position-absolute top-50 start-0 translate-middle-y">
              <button className="btn btn-link" onClick={() => onClick('left')}>
                <span className="material-symbols-rounded">
                  chevron_left
                </span>
              </button>
            </div>
          )
        }
        {
          values.right && (
            <div className="position-absolute top-50 end-0 translate-middle-y">
              <button className="btn btn-link" onClick={() => onClick('right')}>
                <span className="material-symbols-rounded">
                  chevron_right
                </span>
              </button>
            </div>
          )
        }
      </div>
    </div>
  )
}

TableModalNavigation.propTypes = {
  values: PropTypes.object,
  onClick: PropTypes.func.isRequired
}

export default TableModalNavigation
