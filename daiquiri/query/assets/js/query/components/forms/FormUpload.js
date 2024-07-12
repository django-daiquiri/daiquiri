import React, { useState } from 'react'
import PropTypes from 'prop-types'

import Template from 'daiquiri/core/assets/js/components/Template'
import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'

import { useStatusQuery } from '../../hooks/queries'
import { useUploadJobMutation } from '../../hooks/mutations'

import File from './common/File'
import Text from './common/Text'

const FormUpload = ({ form, loadJob }) => {

  const [values, setValues] = useState({
    file: null,
    table_name: '',
    run_id: '',
  })
  const [errors, setErrors] = useState({})

  const { data: status } = useStatusQuery()
  const mutation = useUploadJobMutation()

  const handleUpload = () => {
    mutation.mutate({values, setErrors, loadJob})
  }

  const fileLabel = status ? interpolate(gettext('File (max. %s)'), [bytes2human(status.upload_limit)])
                           : gettext('File')

  return (
    <div className="form">
      <h2>{form.label}</h2>
      <Template template={form.template} />

      <div className="sql-form mt-3">
        <File
          label={fileLabel}
          value={values.file}
          errors={errors.file}
          setValue={(file) => setValues({...values, file})}
        />

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
