import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { isEmpty } from 'lodash'

import Tooltip from 'daiquiri/core/assets/js/components/Tooltip'

import { useUserSchemasQuery } from 'daiquiri/metadata/assets/js/hooks/queries'
import { useUserSchemaQuery } from 'daiquiri/query/assets/js/hooks/queries'

const SchemasDropdown = ({ onPaste }) => {
  const { data: schemas } = useUserSchemasQuery()
  const { data: userSchema } = useUserSchemaQuery()

  const [activeItem, setActiveItem] = useState(null)
  const [openSchema, setOpenSchema] = useState(null)
  const [openTable, setOpenTable] = useState(null)
  const [visibleSchemas, setVisibleSchemas] = useState([])
  const [visibleTables, setVisibleTables] = useState([])
  const [visibleColumns, setVisibleColumns] = useState([])

  useEffect(() => {
    if (!isEmpty(schemas)) {
      setOpenSchema(schemas[0])
      setOpenTable(schemas[0].tables[0])

      setVisibleSchemas([...schemas, ...userSchema])
      setVisibleTables(schemas[0].tables)
      setVisibleColumns(schemas[0].tables[0].columns)
    }
  }, [schemas, userSchema])

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

  const getColumnTooltip = (item) => {
    let tooltip = item.description

    if (!isEmpty(item.unit)) {
      tooltip += `</br><b>Unit:</b> ${item.unit}`
    }

    return tooltip
  }

  return (
    <div className="mb-4">
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
                      <Tooltip title={schema.description} placement="left">
                        <button
                          className={classNames('btn btn-link d-flex', {'active': activeItem === schema})}
                          onClick={() => handleClick('schema', schema)}
                          onDoubleClick={() => onPaste(schema)}
                        >
                          <div>{schema.name}</div>
                          {(openSchema.id == schema.id) && <div className="material-symbols-rounded ms-auto">chevron_right</div>}
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
                      <Tooltip title={table.description} placement="left">
                        <button
                          className={classNames('btn btn-link d-flex', {'active': activeItem === table})}
                          onClick={() => handleClick('table', table)}
                          onDoubleClick={() => onPaste(table)}
                        >
                          <div>{table.name}</div>
                          {(openTable.id == table.id) && <div className="material-symbols-rounded ms-auto">chevron_right</div>}
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
                      <Tooltip title={getColumnTooltip(column)} placement="left">
                        <button
                          className={classNames('btn btn-link', {'active': activeItem === column})}
                          onClick={() => handleClick('column', column)}
                          onDoubleClick={() => onPaste(column)}
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
      <small className="form-text text-muted">
        {gettext('A double click will paste the schema/table/column into the query field.')}
      </small>
    </div>
  )
}

SchemasDropdown.propTypes = {
  onPaste: PropTypes.func.isRequired
}

export default SchemasDropdown
