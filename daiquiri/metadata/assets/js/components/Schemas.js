import React, { useEffect, useState, useRef } from 'react'
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

  const refListTables = useRef(null)
  const refListColumns = useRef(null)

  const initBrowser = () => {
    if (!isEmpty(schemas)) {
      const schema = schemas[0]
      const table = isEmpty(schemas[0].tables) ? null : schemas[0].tables[0]

      setVisibleSchemas(schemas)

      if (isNil(openSchema)) {
        setOpenSchema(schema)
        setVisibleTables(isNil(schema.tables) ? [] : schema.tables)
      }

      if (isNil(openTable) && table) {
        setOpenTable(table)
        setVisibleColumns(isNil(table.columns) ? [] : table.columns)
      }
    }
  }

  const updateBrowser = () => {
    if (activeItem && activeItem.type) {
      if (activeItem.type == 'schema') {
        // search for the schema and get the first table
        const schema = schemas.find(s => isEqual(s, activeItem))
        const table = (isNil(schema) || isEmpty(schema.tables)) ? null : schema.tables[0]

        if (schema && !isEqual(schema, openSchema)) {
          setOpenSchema(schema)
          setVisibleTables(isNil(schema.tables) ? [] : schema.tables)
        }

        setOpenTable(table)
        if (refListTables.current) {
          refListTables.current.scrollTop = 0
        }
        setVisibleColumns((isNil(table) || isNil(table.columns)) ? [] : table.columns)
        if (refListColumns.current) {
          refListColumns.current.scrollTop = 0
        }

      } else if (activeItem.type == 'table') {
        if (!isNil(activeItem.schema)) {
          // this is a newly created table, search for the schema and table
          const [schema, table] = schemas.reduce((result, schema) => {
            return schema.id == activeItem.schema ? (
              [schema, (schema.tables || []).find(t => isEqual(t, activeItem))]
            ) : result
          }, [] )

          if (schema) {
            setOpenSchema(schema)
            setVisibleTables(schema.tables)
          }

          if (table) {
            setOpenTable(table)
            setVisibleColumns(table.columns)
          }
        } else {
          setOpenTable(activeItem)
          setVisibleColumns(activeItem.columns)
          if (refListColumns.current) {
              refListColumns.current.scrollTop = 0
          }
        }

      } else if (activeItem.type == 'column') {
        if (!isNil(activeItem.table)) {
          // this is a newly created column, search for the schema and table
          const [schema, table] = schemas.reduce((result, schema) => {
            const table = (schema.tables || []).find(t => (t.id == activeItem.table))
            return isNil(table) ? result : [schema, table]
          }, [])

          if (schema) {
            setOpenSchema(schema)
            setVisibleTables(schema.tables)
          }

          if (table) {
            setOpenTable(table)
            setVisibleColumns(table.columns)
          }
        }
      }
    }
  }

  useEffect(() => initBrowser(), [schemas])
  useEffect(() => updateBrowser(activeItem), [schemas, activeItem])

  const isEqual = (a, b) => a && b && (isNil(a.id) ? (a.name == b.name) : (a.id == b.id))
  const isActive = (type, item) => activeItem && activeItem.type == type && isEqual(activeItem, item)

  const handleClick = (type, item) => {
    if (!isActive(type, item)) {
      setActiveItem({ type, ...item })
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
                    <Tooltip tooltip={getTooltip('schema', schema)}>
                      <button
                        className={classNames('btn btn-link d-flex', {'active': isActive('schema', schema)})}
                        onClick={() => handleClick('schema', schema)}
                        onDoubleClick={() => handleDoubleClick('schema', schema)}
                      >
                        <div>{schema.name}</div>
                        {
                          openSchema && (isEqual(openSchema, schema)) && (
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
            <ul className="dq-browser-list" ref={refListTables}>
              {
                visibleTables.map((table, index) => (
                  <li key={index}>
                    <Tooltip tooltip={getTooltip('table', table)}>
                      <button
                        className={classNames('btn btn-link d-flex', {'active': isActive('table', table)})}
                        onClick={() => handleClick('table', table)}
                        onDoubleClick={() => handleDoubleClick('table', table)}
                      >
                        <div>{table.name}</div>
                        {
                          openTable && (isEqual(openTable, table)) && (
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
            <ul className="dq-browser-list" ref={refListColumns}>
              {
                visibleColumns.map((column, index) => (
                  <li key={index}>
                    <Tooltip tooltip={getTooltip('column', column)}>
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
