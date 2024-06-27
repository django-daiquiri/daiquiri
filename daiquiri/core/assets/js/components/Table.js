import React from 'react'
import PropTypes from 'prop-types'
import { isEmpty } from 'lodash'

import TableFooter from './TableFooter'
import TableHeader from './TableHeader'
import TablePane from './TablePane'

const Table = ({ columns, rows, pageSizes, params, setParams }) => {
  const show = !(isEmpty(columns) || isEmpty(rows))
  const pageCount = rows.count / params.page_size

  return show && (
    <div className="dq-table">
      <TableHeader
        pageCount={pageCount}
        params={params}
        setParams={setParams}
      />
      <TablePane
        columns={columns}
        rows={rows}
        params={params}
        setParams={setParams}
      />
      <TableFooter
        rowCount={rows.count}
        pageCount={pageCount}
        pageSizes={pageSizes}
        params={params}
        setParams={setParams}
      />
    </div>
  )
}

Table.defaultProps = {
  columns: [],
  rows: {},
  pageSizes: [10, 20, 100]
}

Table.propTypes = {
  columns: PropTypes.array,
  rows: PropTypes.object,
  pageSizes: PropTypes.array,
  params: PropTypes.object.isRequired,
  setParams: PropTypes.func.isRequired
}

export default Table
