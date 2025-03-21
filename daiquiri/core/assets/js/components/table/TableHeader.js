import React, { useState } from 'react'
import PropTypes from 'prop-types'
import classnames from 'classnames'

import { useDebouncedCallback } from 'use-debounce'

const TableHeader = ({ pageCount, params, setParams }) => {

  const [searchInput, setSearchInput] = useState('')

  const isFirstPage = params.page == 1
  const isLastPage = params.page == pageCount

  const handleSearch = useDebouncedCallback(() => setParams({...params, search: searchInput}), 500)

  const handleFirst = () => setParams({...params, page: 1})
  const handlePrevious = () => setParams({...params, page: params.page - 1})
  const handleNext = () => setParams({...params, page: params.page + 1})
  const handleLast = () => setParams({...params, page: pageCount })
  const handleReset = () => {
    setSearchInput('')
    setParams({page: 1, page_size: 10})
  }

  // eslint-disable-next-line react/prop-types
  const PageItem = ({label, disabled, onClick}) => (
    <li className={classnames('page-item', { disabled })}>
      <span className="page-link" onClick={onClick}>
        {label}
      </span>
    </li>
  )

  return (
    <div className="dq-table-header d-md-flex">
      <input
        type="text"
        className="form-control flex-grow-1 mb-3"
        placeholder={gettext('Filter')}
        value={searchInput}
        onChange={(event) => {
          setSearchInput(event.target.value)
          handleSearch()
        }}
      />

      <ul className="pagination">
        <PageItem label={gettext('First')} onClick={handleFirst} disabled={isFirstPage} />
        <PageItem label={gettext('Previous')} onClick={handlePrevious} disabled={isFirstPage} />
        <PageItem label={gettext('Next')} onClick={handleNext} disabled={isLastPage} />
        <PageItem label={gettext('Last')} onClick={handleLast} disabled={isLastPage} />
      </ul>

      <ul className="pagination">
        <PageItem label={gettext('Reset')} onClick={handleReset} />
      </ul>
    </div>
  )
}

TableHeader.propTypes = {
  pageCount: PropTypes.number.isRequired,
  params: PropTypes.object.isRequired,
  setParams: PropTypes.func.isRequired
}

export default TableHeader
