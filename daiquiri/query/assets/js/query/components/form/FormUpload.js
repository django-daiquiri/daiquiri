import React from 'react'
import PropTypes from 'prop-types'

import Template from 'daiquiri/core/assets/js/components/Template'
import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'

import { useStatusQuery } from '../../hooks/query'

const FormUpload = ({ form }) => {

  const { data: status } = useStatusQuery()

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
            <label htmlFor="table-name" className="form-label">{gettext('Table name')}</label>
            <input type="text" className="form-control" id="table-name"></input>
          </div>
          <div className="col-md-2">
            <label htmlFor="table-name" className="form-label">{gettext('Run id')}</label>
            <input type="text" className="form-control" id="table-name"></input>
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
  form: PropTypes.object.isRequired
}

export default FormUpload
