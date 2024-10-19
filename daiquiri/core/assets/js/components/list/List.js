import React from 'react'
import PropTypes from 'prop-types'

import ListHeader from './ListHeader'
import ListFooter from './ListFooter'
import ListTable from './ListTable'

const List = ({ columns, rows, ordering, count, onSearch, onNext, onReset, headerChildren }) => {
  return (
    <div className="dq-list mb-3">
      <ListHeader count={count} onSearch={onSearch} onReset={onReset}>
        {headerChildren}
      </ListHeader>
      <ListTable columns={columns} rows={rows} ordering={ordering} />
      <ListFooter onNext={onNext} />
    </div>
  )
}

List.propTypes = {
  columns: PropTypes.array.isRequired,
  rows: PropTypes.array.isRequired,
  ordering: PropTypes.string,
  count: PropTypes.string,
  onSearch: PropTypes.func,
  onNext: PropTypes.func,
  onReset: PropTypes.func,
  headerChildren: PropTypes.node
}

export default List
