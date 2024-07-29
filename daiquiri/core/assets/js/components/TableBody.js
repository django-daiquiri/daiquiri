import React from 'react'
import PropTypes from 'prop-types'

const TableBody = ({ columns, rows }) => {
  return (
    <tbody>
      {
        rows.results && rows.results.map((row, rowIndex) => (
          <tr key={rowIndex}>
            {
              columns.map((column, columnIndex) => (
                <td key={columnIndex}>
                  <div className="dq-table-cell">
                    {row[columnIndex]}
                  </div>
                </td>
              ))
            }
          </tr>
        ))
      }
    </tbody>
  )
}

TableBody.propTypes = {
  columns: PropTypes.array.isRequired,
  rows: PropTypes.object.isRequired
}

export default TableBody
