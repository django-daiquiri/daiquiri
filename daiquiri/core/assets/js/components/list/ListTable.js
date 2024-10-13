import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { isNil } from 'lodash'

const ListTable = ({ columns, rows, ordering }) => {
  return (
    <table className="table">
      <thead>
        <tr>
        {
          columns.map((column, columnIndex) => (
            <th key={columnIndex} style={{ width: column.width }}>
              {column.label}
              {
                !isNil(column.onOrder) && (
                  <div className="ordering" onClick={() => column.onOrder(column)}>
                    <div className={classNames('ordering-up material-symbols-rounded', {
                      on: ordering == '-' + column.name,
                      off: ordering == column.name
                    })}>arrow_drop_up</div>
                    <div className={classNames('ordering-down material-symbols-rounded', {
                      on: ordering == column.name,
                      off: ordering == '-' + column.name
                    })}>arrow_drop_down</div>
                  </div>
                )
              }
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
