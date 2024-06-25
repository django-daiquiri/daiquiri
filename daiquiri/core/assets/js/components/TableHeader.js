import React from 'react'
import PropTypes from 'prop-types'
import classnames from 'classnames'

const TableHeader = ({ count, params, setParams }) => {

  const lastPage = count / params.page_size
  const isFirstPage = params.page == 1
  const isLastPage = params.page == lastPage

  const handleFirst = () => setParams({...params, page: 1})
  const handlePrevious = () => setParams({...params, page: params.page - 1})
  const handleNext = () => setParams({...params, page: params.page + 1})
  const handleLast = () => setParams({...params, page: lastPage })
  const handleReset = () => setParams({page: 1, page_size: 10})

  // eslint-disable-next-line react/prop-types
  const PageItem = ({label, disabled, onClick}) => (
    <li className={classnames('page-item', { disabled })}>
      <span className="page-link" onClick={onClick}>
        {label}
      </span>
    </li>
  )

  return (
    <div className="dq-table-header">
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
  count: PropTypes.number,
  params: PropTypes.object.isRequired,
  setParams: PropTypes.func.isRequired
}

export default TableHeader
