import React, { useEffect, useState } from 'react'

import { useUpdateMetadataMutation } from '../hooks/mutations'
import { useMetadataQuery, useManagementFunctionsQuery, useManagementSchemasQuery } from '../hooks/queries'

import Functions from './Functions'
import Schemas from './Schemas'

import EditSchema from './EditSchema'
import EditTable from './EditTable'
import EditColumn from './EditColumn'
import EditFunction from './EditFunction'

const Management = () => {
  const [activeItem, setActiveItem] = useState(null)
  const [values, setValues] = useState({})
  const [errors, setErrors] = useState({})

  const { data: schemas } = useManagementSchemasQuery()
  const { data: functions } = useManagementFunctionsQuery()

  const { data: metadata } = useMetadataQuery(activeItem || {})

  const mutation = useUpdateMetadataMutation()

  useEffect(() => setValues(metadata), [metadata])

  const handleSubmit = (type, values) => {
    mutation.mutate({ values, type, setErrors })
  }

  return (
    <div>
      <h1>
        {gettext('Metadata management')}
      </h1>
      <p>
        <small className="text-muted">
          {gettext('Please click on a schema, a table, a column or a function to show or edit its metadata.')}
        </small>
      </p>
      <div className="row">
        <div className="col-md-9">
          <Schemas
            schemas={schemas}
            activeItem={activeItem}
            setActiveItem={setActiveItem} />
        </div>
        <div className="col-md-3">
          <Functions
            functions={functions}
            activeItem={activeItem}
            setActiveItem={setActiveItem} />
        </div>
      </div>
      {
        values && values.type == 'schema' && (
          <EditSchema values={values} errors={errors} setValues={setValues} onSubmit={handleSubmit}/>
        )
      }
      {
        values && values.type == 'table' && (
          <EditTable values={values} errors={errors} setValues={setValues} onSubmit={handleSubmit}/>
        )
      }
      {
        values && values.type == 'column' && (
          <EditColumn values={values} errors={errors} setValues={setValues} onSubmit={handleSubmit}/>
        )
      }
      {
        values && values.type == 'function' && (
          <EditFunction values={values} errors={errors} setValues={setValues} onSubmit={handleSubmit}/>
        )
      }
    </div>
  )
}

export default Management
