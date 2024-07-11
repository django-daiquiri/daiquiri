import React from 'react'
import PropTypes from 'prop-types'

import { useUserSchemasQuery } from 'daiquiri/metadata/assets/js/hooks/queries'
import { useUserSchemaQuery } from '../../../hooks/queries'

const SchemaDropdown = ({ }) => {
  const { data: schemas } = useUserSchemasQuery()
  const { data: userSchema } = useUserSchemaQuery()

  console.log(schemas)
  console.log(userSchema)

  return (
    <div className="card mb-4">
      <div className="dq-browser">
        <div className="row g-0">
          <div className="col-md-4">
            <div className="dq-browser-title">
              {gettext('Schemas')}
            </div>
            <ul className="dq-browser-list">
              <li><button className="btn btn-link" onClick={()=> {}}>Lorem ipsum dolor sit amet, consetetur sadipscing elitr</button></li>
            </ul>
          </div>
          <div className="col-md-4">
            <div className="dq-browser-title">
              {gettext('Tables')}
            </div>
            <ul className="dq-browser-list">
              <li><button className="btn btn-link" onClick={()=> {}}>Lorem</button></li>
            </ul>
          </div>
          <div className="col-md-4">
            <div className="dq-browser-title">
              {gettext('Columns')}
            </div>
            <ul className="dq-browser-list">
              <li><button className="btn btn-link" onClick={()=> {}}>Lorem</button></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

SchemaDropdown.propTypes = {

}

export default SchemaDropdown
