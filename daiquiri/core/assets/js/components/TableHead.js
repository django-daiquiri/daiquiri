import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

const TableHead = ({ columns, params, setParams }) => {
  const tooltips = true
  const ordering = params.ordering || ''

  const handleOrdering = (column) => {
    setParams({...params, ordering: (ordering == column.name) ? '-' + column.name : column.name})
  }

  return (
    <thead>
      <tr>
        {
          columns.map((column, columnIndex) => (
            <th key={columnIndex}>
              <div className="dq-table-cell">
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
                    <div className="info">
                      <span className="material-symbols-rounded align-middle text-body-tertiary">help</span>
                    </div>
                  )
                }
                <div className="order" onClick={() => handleOrdering(column)}>
                  <span className={classNames('material-symbols-rounded align-middle', {
                    'text-body-tertiary': ![column.name, '-' + column.name].includes(ordering)
                  })}>
                    {
                      ordering == '-' + column.name ? (
                        'expand_less'
                      ) : (
                        'expand_more'
                      )
                    }
                  </span>
                </div>
                {
                  columnIndex < columns.length -1 && (
                    <div className="handle"></div>
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