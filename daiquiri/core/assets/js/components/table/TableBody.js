import React from 'react'
import PropTypes from 'prop-types'
import { isEmpty } from 'lodash'

import TableCell from './TableCell'

const TableBody = ({ columns, rows }) => {
  return (
    <tbody>
      {
        isEmpty(rows.results) ? (
          <td>
            <div className="dq-table-cell">
              {gettext('No rows were retrieved.')}
            </div>
          </td>
        ) : rows.results.map((row, rowIndex) => (
          <tr key={rowIndex}>
            {
              columns.map((column, columnIndex) => (
                <td key={columnIndex}>
                  <TableCell column={column} value={row[columnIndex]} />
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
