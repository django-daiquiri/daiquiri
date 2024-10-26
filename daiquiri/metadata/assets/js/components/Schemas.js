import React, { useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { isEmpty, isNil } from 'lodash'

import Tooltip from 'daiquiri/core/assets/js/components/Tooltip'

const Schemas = ({ schemas, activeItem, setActiveItem, getTooltip, onDoubleClick }) => {
  const [openSchema, setOpenSchema] = useState(null)
  const [openTable, setOpenTable] = useState(null)
  const [visibleSchemas, setVisibleSchemas] = useState([])
  const [visibleTables, setVisibleTables] = useState([])
  const [visibleColumns, setVisibleColumns] = useState([])

  useEffect(() => {
    if (!isEmpty(schemas)) {
      setVisibleSchemas(schemas)

      if (isNil(openSchema)) {
        setOpenSchema(schemas[0])
        setVisibleTables(schemas[0].tables)
      }

      if (isNil(openTable)) {
        setOpenTable(schemas[0].tables[0])
        setVisibleColumns(schemas[0].tables[0].columns)
      }
    }
  }, [schemas])

  const isActive = (type, item) => {
    return activeItem && activeItem.type == type && activeItem.id == item.id
  }

  const handleClick = (type, item) => {
    if (item != activeItem) {
      setActiveItem(item)
    }
    if (type == 'schema' && item != openSchema) {
      setOpenSchema(item)
      setOpenTable(item.tables[0])
      setVisibleTables(item.tables)
      setVisibleColumns(item.tables[0].columns)
    }
    if (type == 'table' && item != openTable) {
      setOpenTable(item)
      setVisibleColumns(item.columns)
    }
  }

  const handleDoubleClick = (type, item) => onDoubleClick(type, item)

  return schemas && (
    <div className="card">
      <div className="dq-browser">
        <div className="row g-0">
          <div className="col-md-4">
            <div className="dq-browser-title">
              {gettext('Schemas')}
            </div>
            <ul className="dq-browser-list">
              {
                visibleSchemas.map((schema, index) => (
                  <li key={index}>
                    <Tooltip tooltip={getTooltip(schema)}>
                      <button
                        className={classNames('btn btn-link d-flex', {'active': isActive('schema', schema)})}
                        onClick={() => handleClick('schema', schema)}
                        onDoubleClick={() => handleDoubleClick('schema', schema)}
                      >
                        <div>{schema.name}</div>
                        {
                          openSchema && (openSchema.id == schema.id) && (
                            <div className="ms-auto"><i className="bi bi-chevron-right"></i></div>
                          )
                        }
                      </button>
                    </Tooltip>
                  </li>
                ))
              }
            </ul>
          </div>
          <div className="col-md-4">
            <div className="dq-browser-title">
              {gettext('Tables')}
            </div>
            <ul className="dq-browser-list">
              {
                visibleTables.map((table, index) => (
                  <li key={index}>
                    <Tooltip tooltip={getTooltip(table)}>
                      <button
                        className={classNames('btn btn-link d-flex', {'active': isActive('table', table)})}
                        onClick={() => handleClick('table', table)}
                        onDoubleClick={() => handleDoubleClick('table', table)}
                      >
                        <div>{table.name}</div>
                        {
                          openTable && (openTable.id == table.id) && (
                            <div className="ms-auto"><i className="bi bi-chevron-right"></i></div>
                          )
                        }
                      </button>
                    </Tooltip>
                  </li>
                ))
              }
            </ul>
          </div>
          <div className="col-md-4">
            <div className="dq-browser-title">
              {gettext('Columns')}
            </div>
            <ul className="dq-browser-list">
              {
                visibleColumns.map((column, index) => (
                  <li key={index}>
                    <Tooltip tooltip={getTooltip(column)}>
                      <button
                        className={classNames('btn btn-link', {'active': isActive('column', column)})}
                        onClick={() => handleClick('column', column)}
                        onDoubleClick={() => handleDoubleClick('column', column)}
                      >
                        {column.name}
                      </button>
                    </Tooltip>
                  </li>
                ))
              }
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

Schemas.defaultProps = {
  getTooltip: () => {},
  onDoubleClick: () => {}
}

Schemas.propTypes = {
  schemas: PropTypes.array,
  activeItem: PropTypes.object,
  setActiveItem: PropTypes.func,
  getTooltip: PropTypes.func,
  onDoubleClick: PropTypes.func
}

export default Schemas
