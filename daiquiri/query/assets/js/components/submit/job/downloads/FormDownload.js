import React, { useState } from 'react'
import PropTypes from 'prop-types'

import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'
import Input from 'daiquiri/core/assets/js/components/form/Input'
import Select from 'daiquiri/core/assets/js/components/form/Select'

const FormDownload = ({ jobId, downloadForm, downloadJobs, onSubmit }) => {

  const form = downloadForm.form

  const initialValues = form.fields ?
    Object.fromEntries(
      form.fields.filter(field => field.type != 'submit')
                 .map(field => [field.key, field.default_value || ''])
    ) : {}

  const [values, setValues] = useState(initialValues)

  const [showSpinner, setShowSpinner] = useState(false);

  const handleClick = () => {
    setShowSpinner(true)
    onSubmit(values)
    setTimeout(() => {setShowSpinner(false)}, 2000)
  }

  const hasIncompleteJobs = downloadJobs.some(job => job.phase != 'COMPLETED' && job.phase != 'ERROR')

  const formDownloadJobs = downloadJobs?.filter((job) => job.key == downloadForm.key)

  const handleDownload = (downloadJob) => {
    const url = `/query/api/jobs/${jobId}/download/${downloadJob.key}/${downloadJob.id}/?download=true`
    window.location.href = url
  }

  const renderJob = (downloadJob) => {
    switch (downloadJob.phase) {
      case 'COMPLETED':
        return downloadJob.size != 0 ? (
          <li key={downloadJob.id} className="list-group-item">
            <div className="row">
            {
              form.fields && form.fields.map((field, index) => (
                <div key={index} className={field.width ? `col-md-${field.width}` : 'col-md-12'}>
                {field.type == 'submit' ? (
                    <button className="btn btn-link text-start"
                            onClick={() => handleDownload(downloadJob)}>
                      <i className="bi bi-download"></i>&nbsp;
                      ({bytes2human(downloadJob.size)})
                    </button>
                  ) : (
                    downloadJob[field.key]
                  )
                }
                </div>)
              )
            }
          </div>
          </li>
        ) : ('')
      case 'ERROR':
        return (
          <li key={downloadJob.id} className="list-group-item">
              <div className="row">
              {
                form.fields && form.fields.map((field, index) => (
                  <div key={index} className={field.width ? `col-md-${field.width}` : 'col-md-12'}>
                  {field.type == 'submit' ? (
                      <span className="text-danger"><i className="bi bi-x-octagon-fill"></i> Error</span>
                    ) : (
                      downloadJob[field.key]
                    )
                  }
                  </div>)
                )
              }
            </div>
          </li>
        )
      }
  }

  return (
    <div className="card mb-4">
      <div className="card-header">
        {form.label}
      </div>
      <div className="card-body">
        <div className="row mb-4">
          <p>{form.description}</p>
        </div>
        <div className="form-group row mb-2">
        {
          form.fields && form.fields.map((field, index) => (
            <div key={index} className={field.width ? `col-md-${field.width}` : 'col-md-12'}>
              {
                ['text', 'number'].includes(field.type) && (
                  <Input
                    type={field.type}
                    label={field.label}
                    help={field.help}
                    value={values[field.key]}
                    onChange={(value) => setValues({...values, [field.key]: value})}
                  />
                )
              }
              {
                field.type == 'select' && (
                  <Select
                    label={field.label}
                    help={field.help}
                    value={values[field.key]}
                    options={field.options}
                    onChange={(value) => setValues({...values, [field.key]: value})} />
                )
              }
              {
                field.type == 'submit' && (
                  <div className="mb-3 d-flex flex-column">
                    <label className="form-label">&nbsp;</label>
                    { showSpinner || hasIncompleteJobs ? (
                      <p className="text-primary">
                        <span>
                        <span className="spinner-border spinner-border-sm">
                        </span>
                          {gettext(' Creating..')}
                        </span>
                      </p>
                    ) : (
                      <button type="button" className="btn btn-primary" onClick={handleClick}>
                        {field.label || gettext('Create file')}
                      </button>
                    )
                    }
                  </div>
                )
              }
            </div>
          ))
        }
      </div>
      <ul className="list-group list-group-flush">
      {
        formDownloadJobs && formDownloadJobs.map((download) => (
          renderJob(download)
        ))
      }
      {
        formDownloadJobs && formDownloadJobs.some(download => download.phase == 'ERROR') && (
          <li key="error-message" className="list-group-item">
            <div className="row">
              <p className="text-danger">
                {gettext('Please contact the maintainers of this site if the errors persist.')}
              </p>
            </div>
          </li>
        )
      }
      </ul>
      </div>
    </div>
  )
}

FormDownload.propTypes = {
  downloadForm: PropTypes.object.isRequired,
  jobId: PropTypes.string.isRequired,
  downloadJobs: PropTypes.array.isRequired,
  onSubmit: PropTypes.func.isRequired
}

export default FormDownload
