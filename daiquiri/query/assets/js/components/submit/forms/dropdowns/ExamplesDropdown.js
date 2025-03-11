import React, { useState } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { isEmpty } from 'lodash'

import Tooltip from 'daiquiri/core/assets/js/components/Tooltip'

import { useUserExamplesQuery } from 'daiquiri/query/assets/js/hooks/queries'

const ExamplesDropdown = ({ onDoubleClick }) => {
  const { data: examples } = useUserExamplesQuery()

  const [activeItem, setActiveItem] = useState(null)
  const [filterValue, setFilterValue] = useState('')

  const handleClick = (item) => {
    if (item != activeItem) {
      setActiveItem(item)
    }
  }

  return (
    <div className="mb-4">
      <div className="card">
        <div className="dq-browser">
          <div className="dq-browser-title">
            {gettext('Examples')}
          </div>
          <div className="dq-browser-filter">
            <input
              type="text"
              className="form-control"
              placeholder={gettext('Filter examples')}
              value={filterValue}
              onChange={(event) => setFilterValue(event.target.value)}>
            </input>
          </div>
          <ul className="dq-browser-list">
            {
              examples && examples.filter(
                (example) => (isEmpty(filterValue) || example.name.includes(filterValue))
              ).map((example) => (
                <li key={example.id}>
                  <Tooltip tooltip={{title: example.description, placement: 'left'}}>
                    <button
                      className={classNames('btn btn-link d-flex', {'active': activeItem === example})}
                      onClick={() => handleClick(example)}
                      onDoubleClick={() => onDoubleClick('example', example)}
                    >
                      <div>{example.name}</div>
                    </button>
                  </Tooltip>
                </li>
              ))
            }
          </ul>
        </div>
      </div>
      <small className="form-text text-muted">
        {gettext('A double click will replace the content of the query field with the example.')}
      </small>
    </div>
  )
}

ExamplesDropdown.propTypes = {
  onDoubleClick: PropTypes.func.isRequired
}

export default ExamplesDropdown
