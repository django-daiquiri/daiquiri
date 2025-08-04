import React, {useState, useEffect} from 'react'
import PropTypes from 'prop-types'

import { isNil } from 'lodash'

import { useTableColumnsQuery, useTableRowsQuery } from '../hooks/queries'

import DaiquiriTable from 'daiquiri/core/assets/js/components/table/Table'

const Table = ({ schema, table, search }) => {
  const initialParams = {
    schema,
    table,
    ...(search && { search }),
    page: 1,
    page_size: 10,
  }

  const [params, setParams] = useState(initialParams)

  useEffect(() => {
    // Get URL parameters
    const urlParams = new URLSearchParams(window.location.search)
    const columns = urlParams.getAll('column')
    const search = urlParams.get('search')

    if (columns.length > 0) {
      setParams(prev => ({
        ...prev,
        column: columns
      }))
    }
    if (search) {
      setParams(prev => ({
        ...prev,
        search
      }))
    }
  }, [])

  const setParamsForServe = (params) => {
    if (isNil(params.schema) || isNil(params.table)) {
      params.schema = initialParams.schema
      params.table = initialParams.table
      params.search = initialParams.search
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
  table: PropTypes.string.isRequired,
  search: PropTypes.string,
}

export default Table
