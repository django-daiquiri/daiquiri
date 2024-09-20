import React from 'react'
import PropTypes from 'prop-types'

import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'

import { useDownloadFormatsQuery, useDownloadJobQuery } from '../../hooks/queries'
import { useSubmitDownloadJobMutation } from '../../hooks/mutations'

const JobDownload = ({ job }) => {
  const mutation = useSubmitDownloadJobMutation()
  const downloadJobId = mutation.data && mutation.data.id

  const { data: downloadFormats } = useDownloadFormatsQuery()
  const { data: downloadJob} = useDownloadJobQuery(job.id, 'table', downloadJobId)

  const handleSubmit = (downloadFormat) => {
    mutation.mutate({ job, downloadKey: 'table', downloadFormatKey: downloadFormat.key })
  }

  const getDownloadJobInfo = () => {
    switch (downloadJob.phase) {
    case 'QUEUED':
      return (
        <p className="text-info-emphasis">
          {gettext('The download has been queued on the server.')}
        </p>
      )
    case 'EXECUTING':
      return (
        <p className="text-info-emphasis">
          {interpolate(gettext('The file is currently created on the server (current size: %s).'),
                               [bytes2human(downloadJob.size)])}
          {' '}
          {gettext('Once completed, the download will start automatically.')}
        </p>
      )
    case 'COMPLETED':
      return (
        <p className="text-success">
          {gettext('The file was successfully created on the server, the download should start now.')}
        </p>
      )
    case 'ERROR':
      return (
        <p className="text-danger">
          {gettext('An error occured while creating the file.')}
          {' '}
          {gettext('Please contact the maintainers of this site, if the problem persists.')}
        </p>
      )
    default:
      return null
    }
  }

  return job.phase == 'COMPLETED' ? (
    <div>
      <p>
        {gettext('For further processing of the data, you can download the results table' +
                 ' to your local machine. For this file several formats are available.' +
                 ' Please choose a format for the download from the list below.')}
      </p>

      <h4>{gettext('Download table')}</h4>

      {
        downloadFormats && downloadFormats.map((downloadFormat, index) => (
          <div key={index} className="row">
            <div className="col-md-3">
              <p>
                <button className="btn btn-link text-start" onClick={() => handleSubmit(downloadFormat)}>
                  {downloadFormat.label}
                </button>
              </p>
            </div>
            <div className="col-md-9">
              <p>
                {downloadFormat.help}
              </p>
            </div>
          </div>
        ))
      }

      {
        downloadJob && (
          <div>
            {getDownloadJobInfo()}
          </div>
        )
      }
    </div>
  ) : (
    <p className="text-danger">The query job did not complete successfully.</p>
  )
}

JobDownload.propTypes = {
  job: PropTypes.object.isRequired
}

export default JobDownload
