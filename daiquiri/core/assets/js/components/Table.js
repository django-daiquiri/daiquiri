import React from 'react'
import PropTypes from 'prop-types'

import TableHeader from './TableHeader'
import TablePane from './TablePane'

const Table = ({ columns, rows, params, setParams }) => {
  return (
    <div className="dq-table">
      <TableHeader count={rows.count} params={params} setParams={setParams} />
      <TablePane columns={columns} rows={rows} params={params} setParams={setParams} />
    </div>
  )
}

Table.defaultProps = {
  columns: [],
  rows: {},
}

Table.propTypes = {
  columns: PropTypes.array,
  rows: PropTypes.object,
  params: PropTypes.object.isRequired,
  setParams: PropTypes.func.isRequired
}

export default Table
