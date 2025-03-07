import React, { useState } from 'react'
import { renderToString } from 'react-dom/server'
import { isNumber } from 'lodash'
import PropTypes from 'prop-types'

import Ordering from 'daiquiri/core/assets/js/components/Ordering'
import Template from 'daiquiri/core/assets/js/components/Template'
import Tooltip from 'daiquiri/core/assets/js/components/Tooltip'

import TableHandle from './TableHandle'

const TableHead = ({ columns, params, setParams }) => {
  const ordering = params.ordering || ''

  const [widths, setWidths] = useState(columns.map((column) => {
    return isNumber(column.width) ? column.width : 200
  }))

  const handleOrdering = (column) => {
    setParams({...params, ordering: (ordering == column.name) ? '-' + column.name : column.name})
  }

  const getTooltip = (column) => ({
    placement: 'bottom',
    title: renderToString(
      <div>
        <p className="mb-1">
          <strong className="mb-1">{column.name}</strong>
        </p>
        {column.description && getTooltipParagraph(gettext('Description'), column.description)}
        {column.unit && getTooltipParagraph(gettext('Unit'), column.unit)}
        {column.ucd && getTooltipParagraph(gettext('UCD'), column.ucd)}
        {column.datatype && getTooltipParagraph(gettext('Data type'), column.datatype)}
        {column.arraysize && getTooltipParagraph(gettext('Array size'), column.arraysize)}
        {column.principal && getTooltipParagraph(null, gettext('This column is considered a core part of the service.'))}
        {column.indexed && getTooltipParagraph(null, gettext('This column is indexed.'))}
        {column.std && getTooltipParagraph(null, gettext('This column is defined by a standard.'))}
      </div>
    )
  })

  const getTooltipParagraph = (label, text) => (
    <p className="mb-0">
      {label && <strong>{label}:</strong>} <Template template={text.toString()} />
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
                <Tooltip tooltip={getTooltip(column)}>
                  <i className="bi bi-question-circle text-body-tertiary info me-1"></i>
                </Tooltip>
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
