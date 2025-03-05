import React, { useEffect, useState } from 'react'
import { isEmpty } from 'lodash'

import { useCreateMetadataMutation, useUpdateMetadataMutation, useDiscoverMetadataMutation } from '../hooks/mutations'
import { useMetadataQuery, useManagementFunctionsQuery, useManagementSchemasQuery } from '../hooks/queries'

import { useModal } from 'daiquiri/core/assets/js/hooks/modal'

import Functions from './Functions'
import Schemas from './Schemas'

import AddButton from './AddButton'
import AddModal from './AddModal'
import EditSchema from './EditSchema'
import EditTable from './EditTable'
import EditColumn from './EditColumn'
import EditFunction from './EditFunction'

const Management = () => {
  const [activeItem, setActiveItem] = useState(null)
  const [success, setSuccess] = useState(null)
  const [values, setValues] = useState({})
  const [errors, setErrors] = useState({})

  const modal = useModal()

  const { data: schemas } = useManagementSchemasQuery()
  const { data: functions } = useManagementFunctionsQuery()

  const { data: metadata } = useMetadataQuery(activeItem || {})

  const createMutation = useCreateMetadataMutation()
  const updateMutation = useUpdateMetadataMutation()
  const discoverMutation = useDiscoverMetadataMutation()

  useEffect(() => setValues({ ...metadata }), [metadata])

  const handleModal = (type) => {
    setValues({
      type,
      schema: isEmpty(schemas) ? null : (activeItem?.type == 'schema' ? activeItem.id : schemas[0].id),
      table: (isEmpty(schemas) || isEmpty(schemas[0].tables)) ? null : (activeItem?.type == 'table' ? activeItem.id : schemas[0].tables[0].id),
      query_string: '',
      discover: true
    })
    modal.show()
  }

  const handleCreate = () => {
    createMutation.mutate({ values, modal, setErrors, setActiveItem })
  }

  const handleDiscover = () => {
    discoverMutation.mutate({ values, setValues })
  }

  const handleUpdate = () => {
    updateMutation.mutate({ success, values, setSuccess, setErrors })
  }

  return (
    <div>
      <h1>
        {gettext('Metadata management')}
      </h1>
      <div className="d-flex align-items-center mb-2">
        <small className="text-muted">
          {gettext('Please click on a schema, a table, a column or a function to show or edit its metadata.')}
        </small>
        <AddButton onClick={handleModal} />
      </div>
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
        values && values.id && values.type == 'schema' && (
          <EditSchema
            values={values}
            errors={errors}
            success={success}
            setValues={setValues}
            onSave={handleUpdate} />
        )
      }
      {
        values && values.id && (values.type == 'table' || values.type == 'view') && (
          <EditTable
            values={values}
            errors={errors}
            success={success}
            setValues={setValues}
            onDiscover={handleDiscover}
            onSave={handleUpdate} />
        )
      }
      {
        values && values.id && values.type == 'column' && (
          <EditColumn
            values={values}
            errors={errors}
            success={success}
            setValues={setValues}
            onDiscover={handleDiscover}
            onSave={handleUpdate}
          />
        )
      }
      {
        values && values.id && values.type == 'function' && (
          <EditFunction
            values={values}
            errors={errors}
            success={success}
            setValues={setValues}
            onSave={handleUpdate} />
        )
      }
      <AddModal
        modal={modal}
        values={values}
        errors={errors}
        schemas={(schemas || []).map(schema => ({
          id: schema.id,
          label: schema.name
        }))}
        tables={(schemas || []).reduce((tables, schema) => [...tables, ...(schema.tables || []).map(table => ({
          id: table.id,
          label: `${schema.name}.${table.name}`
        }))], [])}
        setValues={setValues}
        onSubmit={handleCreate}
      />
    </div>
  )
}

export default Management
