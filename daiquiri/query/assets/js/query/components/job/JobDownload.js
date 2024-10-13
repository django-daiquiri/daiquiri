import React from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'

import { jobPhaseClass, jobPhaseMessage } from '../../constants/job'
import { useDownloadJobQuery, useDownloadsQuery } from '../../hooks/queries'
import { useSubmitDownloadJobMutation } from '../../hooks/mutations'

import ArchiveDownload from './downloads/ArchiveDownload'
import FormDownload from './downloads/FormDownload'
import TableDownload from './downloads/TableDownload'

const JobDownload = ({ job }) => {
  const mutation = useSubmitDownloadJobMutation()

  const activeDownloadJob = mutation.data || {}

  const { data: downloads } = useDownloadsQuery()
  const { data: downloadJob} = useDownloadJobQuery(job, activeDownloadJob.key, activeDownloadJob.id)

  const handleSubmit = (downloadKey, data) => {
    mutation.mutate({ job, downloadKey, data })
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
    <div className="query-download">
      <p className="mb-4">
        {gettext('For further processing of the data, you can download the results table' +
                 ' to your local machine. For this file several formats are available.' +
                 ' Please choose a format for the download from the list below.')}
      </p>

      {
        downloads && downloads.map((download, downloadIndex) => {
          if (download.key == 'table') {
            return (
              <TableDownload
                key={downloadIndex}
                onSubmit={(data) => handleSubmit('table', data)}
              />
            )
          } else if (download.key == 'archive') {
            return (
              <ArchiveDownload
                key={downloadIndex}
                columns={job.columns}
                onSubmit={(data) => handleSubmit('archive', data)}
              />
            )
          } else if (!isNil(download.form)) {
            return (
              <FormDownload
                key={downloadIndex}
                form={download.form}
                onSubmit={(data) => handleSubmit(download.key, data)}
              />
            )
          }
        })
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
    <p className={jobPhaseClass[job.phase]}>{jobPhaseMessage[job.phase]}</p>
  )
}

JobDownload.propTypes = {
  job: PropTypes.object.isRequired
}

export default JobDownload
