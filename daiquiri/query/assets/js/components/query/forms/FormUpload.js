import React, { useState } from 'react'
import PropTypes from 'prop-types'

import Template from 'daiquiri/core/assets/js/components/Template'
import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'

import { useFormQuery, useStatusQuery } from 'daiquiri/query/assets/js/hooks/queries'
import { useUploadJobMutation } from 'daiquiri/query/assets/js/hooks/mutations'

import File from 'daiquiri/core/assets/js/components/form/File'
import Input from 'daiquiri/core/assets/js/components/form/Input'

const FormUpload = ({ formKey, loadJob }) => {
  const { data: form } = useFormQuery(formKey)
  const { data: status } = useStatusQuery()
  const mutation = useUploadJobMutation()

  const [values, setValues] = useState({
    file: null,
    table_name: '',
    run_id: '',
  })
  const [errors, setErrors] = useState({})

  const handleUpload = () => {
    mutation.mutate({values, setErrors, loadJob})
  }

  const fileLabel = status ? interpolate(gettext('File (max. %s)'), [bytes2human(status.upload_limit)])
                           : gettext('File')

  return form && (
    <div className="query-form mb-4">
      <h2>{form.label}</h2>
      <Template template={form.template} />

      <div className="upload-form mt-3">
        <File
          label={fileLabel}
          value={values.file}
          errors={errors.file}
          onChange={(file) => setValues({...values, file})}
        />

        <div className="row">
          <div className="col-md-10">
            <Input
              label={gettext('Table name')}
              value={values.table_name}
              errors={errors.table_name}
              onChange={(table_name) => setValues({...values, table_name})}
            />
          </div>
          <div className="col-md-2">
            <Input
              label={gettext('Run id')}
              value={values.run_id}
              errors={errors.run_id}
              onChange={(run_id) => setValues({...values, run_id})}
            />
          </div>
        </div>

        <div className="mt-2">
          <button type="button" className="btn btn-primary me-auto" onClick={() => handleUpload()}>
            {form.submit || gettext('Upload')}
          </button>
        </div>
      </div>
    </div>
  )
}

FormUpload.propTypes = {
  formKey: PropTypes.string.isRequired,
  loadJob: PropTypes.func.isRequired
}

export default FormUpload
