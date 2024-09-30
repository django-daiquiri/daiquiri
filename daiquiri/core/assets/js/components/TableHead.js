import React, { useState } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import TableHandle from './TableHandle'

const TableHead = ({ columns, params, setParams }) => {
  const tooltips = true
  const ordering = params.ordering || ''

  const [widths, setWidths] = useState(columns.map(() => 300))

  const handleOrdering = (column) => {
    setParams({...params, ordering: (ordering == column.name) ? '-' + column.name : column.name})
  }

  return (
    <thead>
      <tr>
        {
          columns.map((column, columnIndex) => (
            <th key={columnIndex} style={{ width: widths[columnIndex] }}>
              <div className="dq-table-cell">
                {
                  columnIndex > 0 && (
                    <TableHandle columnIndex={columnIndex - 1} widths={widths} setWidths={setWidths} />
                  )
                }
                <div className="name">
                  {
                    column.label ? (
                      <span>{column.label}</span>
                    ) : (
                      <span>{column.name}</span>
                    )
                  }
                </div>
                {
                  tooltips && (
                    <div className="info material-symbols-rounded text-body-tertiary">
                      question_mark
                    </div>
                  )
                }
                <div
                  className={classNames('order material-symbols-rounded', {
                    'text-body-tertiary': ![column.name, '-' + column.name].includes(ordering)
                  })}
                  onClick={() => handleOrdering(column)}
                >
                  {
                    ordering == '-' + column.name ? (
                      'expand_less'
                    ) : (
                      'expand_more'
                    )
                  }
                </div>
                {
                  columnIndex < (columns.length - 1) && (
                    <TableHandle columnIndex={columnIndex} widths={widths} setWidths={setWidths} />
                  )
                }
              </div>
            </th>
          ))
        }
      </tr>
    </thead>
  )
}

TableHead.propTypes = {
  columns: PropTypes.array.isRequired,
  params: PropTypes.object.isRequired,
  setParams: PropTypes.func.isRequired
}

export default TableHead
