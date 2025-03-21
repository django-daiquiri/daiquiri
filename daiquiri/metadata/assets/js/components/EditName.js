import React from 'react'
import PropTypes from 'prop-types'

import Input from 'daiquiri/core/assets/js/components/form/Input'

const EditName = ({ person, onChange, onRemove }) => {
  return (
    <div className="d-flex flex-row">
      <div className="flex-grow-1 me-2">
        <Input
          label={gettext('Name')}
          value={person.name || ''}
          onChange={(name) => onChange({ ...person, name })} />
      </div>
      <div className="flex-grow-1 me-2">
        <Input
          label={gettext('First name')}
          value={person.first_name || ''}
          onChange={(first_name) => onChange({ ...person, first_name })} />
      </div>
      <div className="flex-grow-1 me-2">
        <Input
          label={gettext('Last name')}
          value={person.last_name || ''}
          onChange={(last_name) => onChange({ ...person, last_name })} />
      </div>
      <div className="flex-grow-1 me-2">
        <Input
          label={gettext('ORCiD')}
          value={person.orcid || ''}
          onChange={(orcid) => onChange({ ...person, orcid })} />
      </div>
      <div className="align-self-end">
        <button type="button "className="btn btn-outline-danger mb-3" onClick={onRemove}>
          <i className="bi bi-trash"></i>
        </button>
      </div>
    </div>
  )
}

EditName.propTypes = {
  person: PropTypes.object.isRequired,
  onChange: PropTypes.func.isRequired,
  onRemove: PropTypes.func.isRequired
}

export default EditName
