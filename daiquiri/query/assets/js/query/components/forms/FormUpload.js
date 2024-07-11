import React, { useState } from 'react'
import PropTypes from 'prop-types'

import Template from 'daiquiri/core/assets/js/components/Template'
import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'

import { useStatusQuery, useUploadJobMutation } from '../../hooks/queries'

import Text from './common/Text'

const FormUpload = ({ form, loadJob }) => {

  const [values, setValues] = useState({
    table_name: '',
    run_id: '',
  })
  const [errors, setErrors] = useState({})

  const { data: status } = useStatusQuery()
  const mutation = useUploadJobMutation()

  const handleUpload = () => {
    console.log('handleUpload')
  }

  return (
    <div className="form">
      <h2>{form.label}</h2>
      <Template template={form.template} />

      <div className="sql-form mt-3">
        <div className="mb-3">
          <label htmlFor="table-name" className="form-label" dangerouslySetInnerHTML={{
            __html: interpolate(gettext('File (max. %s)'), [bytes2human(status.upload_limit)])
          }} />
          <div className="form-text">
            {gettext('Drag and drop file or click to open a file browser')}
          </div>
        </div>

        <div className="row">
          <div className="col-md-10">
            <Text
              label={gettext('Table name')}
              value={values.table_name}
              errors={errors.table_name}
              setValue={(table_name) => setValues({...values, table_name})}
            />
          </div>
          <div className="col-md-2">
            <Text
              label={gettext('Run id')}
              value={values.run_id}
              errors={errors.run_id}
              setValue={(run_id) => setValues({...values, run_id})}
            />
          </div>
        </div>

        <div className="mt-4">
          <button type="button" className="btn btn-primary me-auto" onClick={() => handleUpload()}>
            {gettext('Upload table')}
          </button>
        </div>
      </div>
    </div>
  )
}

FormUpload.propTypes = {
  form: PropTypes.object.isRequired,
  loadJob: PropTypes.func.isRequired
}

export default FormUpload
