import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { isEmpty, isUndefined } from 'lodash'

import Schemas from 'daiquiri/metadata/assets/js/components/Schemas'

import { useUserSchemasQuery } from 'daiquiri/metadata/assets/js/hooks/queries'
import { useJobsTablesQuery } from 'daiquiri/query/assets/js/hooks/queries'

const SchemasDropdown = ({ onDoubleClick }) => {
  const { data: schemas } = useUserSchemasQuery()
  const { data: userSchema } = useJobsTablesQuery()

  const [activeItem, setActiveItem] = useState(null)

  const getTooltip = (type, item) => {
    return {
      title: (item.description || '') + (isEmpty(item.unit) ? '' : `</br><b>Unit:</b> ${item.unit}`),
      placement: 'left'
    }
  }

  return !isUndefined(schemas) && !isUndefined(userSchema) && (
    <div>
      <Schemas
        schemas={[...schemas, ...userSchema]}
        activeItem={activeItem}
        setActiveItem={setActiveItem}
        getTooltip={getTooltip}
        onDoubleClick={onDoubleClick}
      />
      <small className="form-text text-muted">
        {gettext('A double click will paste the schema/table/column into the query field.')}
      </small>
    </div>
  )
}

SchemasDropdown.propTypes = {
  onDoubleClick: PropTypes.func.isRequired
}

export default SchemasDropdown
