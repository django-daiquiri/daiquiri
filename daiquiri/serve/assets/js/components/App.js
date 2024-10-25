import React, {useState} from 'react'
import PropTypes from 'prop-types'

import { useTableColumnsQuery, useTableRowsQuery } from '../hooks/queries'

import Table from 'daiquiri/core/assets/js/components/table/Table'

const App = ({ schema, table }) => {
  const initialParams = {
    schema,
    table,
    page: 1,
    page_size: 10
  }

  const [params, setParams] = useState(initialParams)

  const { data: columns } = useTableColumnsQuery(params)
  const { data: rows } = useTableRowsQuery(params)

  return (
    <Table
      columns={columns}
      rows={rows}
      params={params}
      setParams={setParams}
    />
  )
}

App.propTypes = {
  schema: PropTypes.string.isRequired,
  table: PropTypes.string.isRequired
}

export default App
