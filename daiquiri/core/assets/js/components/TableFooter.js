import React from 'react'
import PropTypes from 'prop-types'

const TableFooter = ({ rowCount, pageCount, pageSizes, params, setParams }) => {

  const handlePageSizeSelect = (event) => {
    setParams({...params, page_size: event.target.value})
  }

  return (
    <div className="dq-table-footer d-md-flex mt-3">
      <p className="flex-grow-1 mt-md-1 mb-md-1 mb-2">
        {
          params.search ? (
            interpolate(gettext('Page %s of %s (%s rows total, filtering for "%s")'),
                                [params.page, pageCount, rowCount, params.search])
          ) : (
            interpolate(gettext('Page %s of %s (%s rows total)'),
                                [params.page, pageCount, rowCount])
          )
        }
      </p>

      <div>
        <select className="form-select" onChange={handlePageSizeSelect}>
          {
            pageSizes.map((pageSize, index) => (
              <option key={index} value={pageSize}>
                {interpolate(gettext('Show %s of %s rows'), [pageSize, rowCount])}
              </option>
            ))
          }
        </select>
      </div>
    </div>
  )
}

TableFooter.propTypes = {
  rowCount: PropTypes.number.isRequired,
  pageCount: PropTypes.number.isRequired,
  pageSizes: PropTypes.array,
  params: PropTypes.object.isRequired,
  setParams: PropTypes.func.isRequired
}

export default TableFooter
