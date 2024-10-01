import React from 'react'
import PropTypes from 'prop-types'

const TableCell = ({ column, value }) => {
  return (
    <div className="dq-table-cell">
      {value}
    </div>
  )
}

TableCell.propTypes = {
  column: PropTypes.number.isRequired,
  value: PropTypes.array.isRequired
}

export default TableCell
