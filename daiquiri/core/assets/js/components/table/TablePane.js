import React from 'react'
import PropTypes from 'prop-types'

import TableHead from './TableHead'
import TableBody from './TableBody'

const TablePane = ({ columns, rows, params, active, setParams, onClick }) => {

  return (
    <div className="dq-table-pane">
      <table className="table">
        <TableHead
          columns={columns}
          params={params}
          setParams={setParams}
        />
        <TableBody
          columns={columns}
          rows={rows}
          active={active}
          onClick={onClick}
        />
      </table>
    </div>
  )
}

TablePane.propTypes = {
  columns: PropTypes.array.isRequired,
  rows: PropTypes.object.isRequired,
  params: PropTypes.object.isRequired,
  active: PropTypes.object.isRequired,
  setParams: PropTypes.func.isRequired,
  onClick: PropTypes.func.isRequired
}

export default TablePane