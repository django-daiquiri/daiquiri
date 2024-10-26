import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { isEmpty } from 'lodash'

import Tooltip from 'daiquiri/core/assets/js/components/Tooltip'

import { useUserSchemasQuery } from 'daiquiri/metadata/assets/js/hooks/queries'
import { useJobsTablesQuery } from 'daiquiri/query/assets/js/hooks/queries'

const ColumnsDropdown = ({ onDoubleClick }) => {
  const { data: schemas } = useUserSchemasQuery()
  const { data: userSchema } = useJobsTablesQuery()

  const [columns, setColumns] = useState([])
  const [activeItem, setActiveItem] = useState(null)
  const [filterValue, setFilterValue] = useState('')

  useEffect(() => {
    if (!isEmpty(schemas)) {
      setColumns(
        schemas.reduce((schemaAgg, schema) => {
          return [...schemaAgg, ...schema.tables.reduce((tableAgg, table) => {
            return [...tableAgg, ...table.columns.reduce((columnAgg, column) => {
              const c = {...column}
              c.full_name = schema.name + '.' + table.name + '.' + column.name
              c.full_query_strings = table.name
              return [...columnAgg, {
                ...column,
                name: schema.name + '.' + table.name + '.' + column.name,
                query_strings: table.query_strings.concat(column.query_strings)
              }]
            }, [])]
          }, [])]
        }, [])
      )
    }
  }, [schemas, userSchema])

  const handleClick = (item) => {
    if (item != activeItem) {
      setActiveItem(item)
    }
  }

  const getTooltip = (item) => ({
    title: item.description + isEmpty(item.unit) ? '' : `</br><b>Unit:</b> ${item.unit}`,
    placement: 'left'
  })

  return (
    <div className="mb-4">
      <div className="card">
        <div className="dq-browser">
          <div className="dq-browser-title">
            {gettext('Columns')}
          </div>
          <div className="dq-browser-filter">
            <input
              type="text"
              className="form-control"
              placeholder={gettext('Filter columns')}
              value={filterValue}
              onChange={(event) => setFilterValue(event.target.value)}>
            </input>
          </div>
          <ul className="dq-browser-list">
            {
              columns.filter((column) => (isEmpty(filterValue) || column.name.includes(filterValue))).map((column) => (
                <li key={column.id}>
                  <Tooltip tooltip={getTooltip(column)}>
                    <button
                      className={classNames('btn btn-link d-flex', {'active': activeItem === column})}
                      onClick={() => handleClick(column)}
                      onDoubleClick={() => onDoubleClick('column', column)}
                    >
                      <div>{column.name}</div>
                    </button>
                  </Tooltip>
                </li>
              ))
            }
          </ul>
        </div>
      </div>
      <small className="form-text text-muted">
        {gettext('A double click will paste the column into the query field.')}
      </small>
    </div>
  )
}

ColumnsDropdown.propTypes = {
  onDoubleClick: PropTypes.func.isRequired
}

export default ColumnsDropdown
