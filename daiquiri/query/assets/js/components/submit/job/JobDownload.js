import React from 'react'
import PropTypes from 'prop-types'
import { isNil, isEmpty } from 'lodash'

import { jobPhaseClass, jobPhaseMessage } from 'daiquiri/query/assets/js/constants/job'
import { useSubmittedDownloadsQuery, useDownloadFormsQuery } from 'daiquiri/query/assets/js/hooks/queries'
import { useSubmitDownloadJobMutation } from 'daiquiri/query/assets/js/hooks/mutations'

import ArchiveDownload from './downloads/ArchiveDownload'
import FormDownload from './downloads/FormDownload'
import TableDownload from './downloads/TableDownload'

const JobDownload = ({ job }) => {

  const mutation = useSubmitDownloadJobMutation()

  const { data: downloadForms } = useDownloadFormsQuery(job.id)

  const { data: downloadJobs } = useSubmittedDownloadsQuery(job.id) || []

  const handleSubmit = (downloadKey, data) => {
    mutation.mutate({ job, downloadKey, data })
  }

  return job.phase == 'COMPLETED' ? (
    <div className="query-download">
      <p className="mb-4">
        {
          isEmpty(downloadForms) ? gettext('The download of the results is currently not available.') :
          gettext('For further processing of the data, you can create a file from the results table' +
                 ' and then download it to your local machine. For this file several formats are available.' +
                 ' Please choose a format from the list below.')
        }
      </p>

      {
        downloadForms && downloadForms.map((downloadForm, downloadIndex) => {
          if (downloadForm.key == 'table') {
            return (
              <TableDownload
                key={downloadIndex}
                jobId={job.id}
                downloadJobs={downloadJobs || []}
                onSubmit={(data) => handleSubmit('table', data)}
              />
            )
          } else if (downloadForm.key == 'archive') {
            return (
              <ArchiveDownload
                key={downloadIndex}
                jobId={job.id}
                columns={job.columns}
                downloadJobs={downloadJobs || []}
                onSubmit={(data) => handleSubmit('archive', data)}
              />
            )
          } else if (!isNil(downloadForm.form)) {
            return (
              <FormDownload
                key={downloadIndex}
                jobId={job.id}
                downloadForm={downloadForm}
                downloadJobs={downloadJobs || []}
                onSubmit={(data) => handleSubmit(downloadForm.key, data)}
              />
            )
          }
        })
      }

    </div>
  ) : (
    <p className={jobPhaseClass[job.phase]}>{jobPhaseMessage[job.phase]}</p>
  )
}

JobDownload.propTypes = {
  job: PropTypes.object.isRequired
}

export default JobDownload
