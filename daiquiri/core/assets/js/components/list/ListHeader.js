import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { useDebouncedCallback } from 'use-debounce'
import { isEmpty } from 'lodash'

const ListHeader = ({ count, onSearch, onReset, buttons, checkboxes }) => {
  const [searchInput, setSearchInput] = useState('')

  const handleSearch = useDebouncedCallback(() => onSearch(searchInput), 500)

  const handleReset = () => {
    setSearchInput('')
    onReset()
  }

  return (
    <div className="dq-list-header d-md-flex mb-3 align-items-center">
      <input
        type="text"
        className="form-control mb-2 me-5"
        placeholder={gettext('Filter')}
        value={searchInput}
        onChange={(event) => {
          setSearchInput(event.target.value)
          handleSearch()
        }}
      />

      <div className="me-5 mb-2 text-nowrap">
          { count }
      </div>

      {
        !isEmpty(buttons) && (
          <ul className="pagination me-2">
            {
              buttons.map((button, buttonIndex) => (
                <li key={buttonIndex} className="page-item">
                  <span className="page-link text-nowrap" onClick={button.onClick}>
                    {button.label}
                  </span>
                </li>
              ))
            }
          </ul>
        )
      }

      <ul className="pagination">
        <li className="page-item">
          <span className="page-link" onClick={handleReset}>
            {gettext('Reset')}
          </span>
        </li>
      </ul>
    </div>
  )
}

ListHeader.propTypes = {
  count: PropTypes.string,
  onSearch: PropTypes.func,
  onReset: PropTypes.func,
  buttons: PropTypes.array,
  checkboxes: PropTypes.object
}

export default ListHeader
