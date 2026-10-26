import React from 'react'
import PropTypes from 'prop-types'

import Checkbox from 'daiquiri/core/assets/js/components/form/Checkbox'

const GroupAccess = ({ groups, selectedIds, onChange }) => (
  <div className="mb-3">
    <strong className="d-block mb-2">{gettext('Groups with access')}</strong>
    <div className="row row-cols-1 row-cols-md-2 row-cols-xl-3 gy-1">
      {groups.map((group) => (
        <div className="col" key={group.id}>
          <Checkbox
            label={group.name}
            checked={selectedIds.includes(group.id)}
            onChange={(checked) => onChange(checked
              ? [...selectedIds, group.id]
              : selectedIds.filter((id) => id !== group.id)
            )}
          />
        </div>
      ))}
    </div>
  </div>
)

GroupAccess.propTypes = {
  groups: PropTypes.array.isRequired,
  selectedIds: PropTypes.array.isRequired,
  onChange: PropTypes.func.isRequired
}

export default GroupAccess
