import React from 'react'
import PropTypes from 'prop-types'

import { getBasename, getFileUrl, getLinkUrl, getReferenceUrl,
         isModalColumn, isFileColumn, isLinkColumn } from '../../utils/table.js'

const TableCell = ({ column, value, rowIndex, columnIndex, onClick }) => {

  const handleClick = (event) => {
    event.preventDefault()
    event.stopPropagation()
    onClick(rowIndex, columnIndex)
  }

  const renderCell = () => {
    if (column.ucd && column.ucd.includes('meta.ref')) {
      if (isModalColumn(column)) {
        // render the modal
        return (
          <a href={getFileUrl(column, value)} onClick={handleClick}>{value}</a>
        )
      } else if (isFileColumn(column)) {
        // render a file link
        return (
          <a href={getFileUrl(column, value)} target="_blank" rel="noreferrer">{getBasename(value)}</a>
        )
      } else if (isLinkColumn(column)) {
        // render a regular link
        return (
          <a href={getLinkUrl(column, value)} target="_blank" rel="noreferrer">{value}</a>
        )
      } else {
        // render a link to the resolver
        return (
          <a href={getReferenceUrl(column, value)} target="_blank" rel="noreferrer">{value}</a>
        )
      }
    } else {
      // this is not a reference, just render the value
      return value
    }
  }

  return (
    <div className="dq-table-cell" onClick={handleClick}>
      {renderCell()}
    </div>
  )
}

TableCell.propTypes = {
  column: PropTypes.object.isRequired,
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  rowIndex: PropTypes.number.isRequired,
  columnIndex: PropTypes.number.isRequired,
  onClick: PropTypes.func.isRequired
}

export default TableCell