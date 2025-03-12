import React, {useState} from 'react'
import PropTypes from 'prop-types'

import { isNil } from 'lodash'

import { useTableColumnsQuery, useTableRowsQuery } from '../hooks/queries'

import DaiquiriTable from 'daiquiri/core/assets/js/components/table/Table'

const Table = ({ schema, table }) => {
  const initialParams = {
    schema,
    table,
    page: 1,
    page_size: 10
  }

  const [params, setParams] = useState(initialParams)

  const setParamsForServe = (params) => {
    if (isNil(params.schema) || isNil(params.table)) {
      params.schema = initialParams.schema
      params.table = initialParams.table
    }
    return setParams(params)
  }

  const { data: columns } = useTableColumnsQuery(params)
  const { data: rows } = useTableRowsQuery(params)

  return (
    <DaiquiriTable
      columns={columns}
      rows={rows}
      params={params}
      setParams={setParamsForServe}
    />
  )
}

Table.propTypes = {
  schema: PropTypes.string.isRequired,
  table: PropTypes.string.isRequired
}

export default Table
