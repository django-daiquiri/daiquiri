import React from 'react'
import PropTypes from 'prop-types'

const AddButton = ({ onClick }) => {
  return (
    <div className="dropdown ms-auto">
      <button className="btn btn-outline-primary btn-sm dropdown-toggle"
              type="button" data-bs-toggle="dropdown" aria-expanded="false">
        {gettext('Add')}
      </button>
      <ul className="dropdown-menu dropdown-menu-end">
        <li>
          <button className="dropdown-item" onClick={() => onClick('schema')}>
            {gettext('Add schema')}
          </button>
        </li>
        <li>
          <button className="dropdown-item" onClick={() => onClick('table')}>
            {gettext('Add table')}
          </button>
        </li>
        <li>
          <button className="dropdown-item" onClick={() => onClick('column')}>
            {gettext('Add column')}
          </button>
        </li>
        <li>
          <button className="dropdown-item" onClick={() => onClick('function')}>
            {gettext('Add function')}
          </button>
        </li>
      </ul>
    </div>
  )
}

AddButton.propTypes = {
  onClick: PropTypes.func.isRequired
}

export default AddButton
