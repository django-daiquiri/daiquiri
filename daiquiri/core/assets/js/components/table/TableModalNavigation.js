import React from 'react'
import PropTypes from 'prop-types'

const TableModalNavigation = ({ values, onClick }) => {
  return (
    <div className="dq-table-modal-navigation position-absolute z-1 top-0 end-0 mt-3 me-3">
      <div className="position-relative w-100 h-100">
        {
          values.up && (
            <button className="position-absolute top-0 start-50 translate-middle-x btn btn-link mt-1"
                    onClick={() => onClick('up')}>
              <i className="bi bi-caret-up-fill"></i>
            </button>
          )
        }
        {
          values.down && (
            <div className="position-absolute bottom-0 start-50 translate-middle-x btn btn-link mb-1"
                 onClick={() => onClick('down')}>
                <i className="bi bi-caret-down-fill"></i>
            </div>
          )
        }
        {
          values.left && (
            <div className="position-absolute top-50 start-0 translate-middle-y btn btn-link ms-1"
                 onClick={() => onClick('left')}>
                <i className="bi bi-caret-left-fill"></i>
            </div>
          )
        }
        {
          values.right && (
            <div className="position-absolute top-50 end-0 translate-middle-y btn btn-link me-1"
                 onClick={() => onClick('right')}>
                <i className="bi bi-caret-right-fill"></i>
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
