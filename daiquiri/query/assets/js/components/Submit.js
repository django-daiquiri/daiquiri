import React from 'react'
import PropTypes from 'prop-types'

import Form from './submit/forms/Form'
import Forms from './submit/Forms'
import FormSql from './submit/forms/FormSql'
import FormUpload from './submit/forms/FormUpload'
import Job from './submit/job/Job'
import Jobs from './submit/Jobs'
import Status from './submit/Status'

const Submit = ({ formKey, jobId, query, queryLanguage, loadForm, loadJob, loadJobs }) => {
  const getForm = () => {
    switch (formKey) {
      case 'sql':
        return <FormSql formKey={formKey} loadJob={loadJob} query={query} queryLanguage={queryLanguage} />
      case 'upload':
        return <FormUpload formKey={formKey} loadJob={loadJob} />
      default:
        return <Form formKey={formKey} loadJob={loadJob} />
    }
  }

  return (
    <div>
      <h1 className="mb-4">Query interface</h1>

      <div className="row">
        <div className="col-lg-3 order-2 order-lg-1">
          <Status />
          <Forms formKey={formKey} loadForm={loadForm} />
          <Jobs jobId={jobId} loadJob={loadJob} loadJobs={loadJobs} />
        </div>
        <div className="col-lg-9 order-1 order-lg-2">
          {
            jobId && <Job jobId={jobId} loadForm={loadForm} loadJob={loadJob} />
          }
          {
            formKey && getForm()
          }
        </div>
      </div>
    </div>
  )
}

Submit.propTypes = {
  formKey: PropTypes.string,
  jobId: PropTypes.string,
  query: PropTypes.string,
  queryLanguage: PropTypes.string,
  loadForm: PropTypes.func.isRequired,
  loadJob: PropTypes.func.isRequired,
  loadJobs: PropTypes.func.isRequired,
}

export default Submit
