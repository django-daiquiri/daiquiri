import React, { useState } from 'react'
import { renderToString } from 'react-dom/server'
import PropTypes from 'prop-types'

import Ordering from 'daiquiri/core/assets/js/components/Ordering'
import Popover from 'daiquiri/core/assets/js/components/Popover'

import TableHandle from './TableHandle'

const TableHead = ({ columns, params, setParams }) => {
  const tooltips = true
  const ordering = params.ordering || ''

  const [widths, setWidths] = useState(columns.map(() => 300))

  const handleOrdering = (column) => {
    setParams({...params, ordering: (ordering == column.name) ? '-' + column.name : column.name})
  }

  const getPopoverTitle = (column) => renderToString(
    <b>{column.name}</b>
  )

  const getPopoverContent = (column) => renderToString(
    <div>
      {column.description && getPopoverParagraph(gettext('Description'), column.description)}
      {column.unit && getPopoverParagraph(gettext('Unit'), column.unit)}
      {column.ucd && getPopoverParagraph(gettext('UCD'), column.ucd)}
      {column.datatype && getPopoverParagraph(gettext('Data type'), column.datatype)}
      {column.arraysize && getPopoverParagraph(gettext('Array size'), column.arraysize)}
      {column.principal && getPopoverParagraph(null, gettext('This column is considered a core part of the service.'))}
      {column.indexed && getPopoverParagraph(null, gettext('This column is indexed.'))}
      {column.std && getPopoverParagraph(null, gettext('This column is defined by a standard.'))}
    </div>
  )

  const getPopoverParagraph = (label, text) => (
    <p>
      {label && <strong>{label}</strong>} {text}
    </p>
  )

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
                    <Popover title={getPopoverTitle(column)} content={getPopoverContent(column)}>
                      <i className="bi bi-question-circle text-body-tertiary info me-1"></i>
                    </Popover>
                  )
                }
                <Ordering column={column} ordering={ordering} onOrder={handleOrdering} />
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
