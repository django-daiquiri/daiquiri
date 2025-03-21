import React from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import Ordering from 'daiquiri/core/assets/js/components/Ordering'

const ListTable = ({ columns, rows, ordering }) => {
  return (
    <table className="table">
      <thead>
        <tr>
        {
          columns.map((column, columnIndex) => (
            <th key={columnIndex} style={{ width: column.width }}>
              {column.label}
              <Ordering column={column} ordering={ordering} onOrder={column.onOrder}/>
            </th>
          ))
        }
        </tr>
      </thead>
      <tbody>
        {
          rows.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {
                columns.map((column, columnIndex) => (
                  <td key={columnIndex}>
                    {
                      isNil(column.formatter) ? row[column.name] : column.formatter(row)
                    }
                  </td>
                ))
              }
            </tr>
          ))
        }
      </tbody>
    </table>
  )
}

ListTable.propTypes = {
  columns: PropTypes.array.isRequired,
  rows: PropTypes.array.isRequired,
  ordering: PropTypes.string
}

export default ListTable
