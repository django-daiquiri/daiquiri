import React from 'react'
import PropTypes from 'prop-types'

import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'
import { useDownloadFormatsQuery } from 'daiquiri/query/assets/js/hooks/queries'

import Tooltip  from 'daiquiri/core/assets/js/components/Tooltip'

const TableDownload = ({ jobId, downloadJobs, onSubmit }) => {

  const { data: downloadFormats } = useDownloadFormatsQuery()

  const getTooltipCreate = (item) => {
    return {
      title: `Create the .${item.extension} file`,
      placement: 'right'
    }
  }

  const getTooltipDownload = (item) => {
    return {
      title: `Download the .${item.extension} file`,
      placement: 'right'
    }
  }

  const handleDownload = (downloadJob) => {
    const url = `/query/api/jobs/${jobId}/download/table/${downloadJob.id}/?download=true`
    window.location.href = url
  }

  const getDownloadJobInfo = (downloadJob, downloadFormat) => {
    const renderDefault = () => (
      <Tooltip tooltip={getTooltipCreate(downloadFormat)}>
      <button className="btn btn-link text-start"
              onClick={() => onSubmit({
        format_key: downloadFormat.key
      })}>
        <i className="bi bi-file-earmark-plus"></i>&nbsp;
        .{downloadFormat.extension}
      </button>
      </Tooltip>
    )

    if (!downloadJob || !downloadJob.phase) {
      return renderDefault()
    }

    switch (downloadJob.phase) {
    case 'QUEUED':
      return (
        <div>
          <p className="text-primary">
            <span>
            <span className="spinner-border spinner-border-sm">
            </span>
              {gettext(' Queued..')}
            </span>
          </p>
        </div>
      )
    case 'PENDING':
      return (
        <div>
          <p className="text-primary">
            <span>
            <span className="spinner-border spinner-border-sm">
            </span>
              {gettext(' Pending..')}
            </span>
          </p>
        </div>
      )
    case 'EXECUTING':
      return (
        <div>
          <div className="text-primary">
            <span>
            <span className="spinner-border spinner-border-sm">
            </span>
              {gettext(' Creating..')}
            </span>
            <p>
              {interpolate(gettext('(%s)'), [bytes2human(downloadJob.size)])}
            </p>
          </div>
        </div>
      )
    case 'COMPLETED':
      return downloadJob.size > 0 ? (
        <Tooltip tooltip={getTooltipDownload(downloadFormat)}>
          <button className="btn btn-link text-start"
                  onClick={() => handleDownload(downloadJob)}>
            <i className="bi bi-download"></i>&nbsp;
            .{downloadFormat.extension} ({bytes2human(downloadJob.size)})
          </button>
        </Tooltip>
      ) : (
        renderDefault()
      )
    case 'ERROR':
      return (
        <div>
        {renderDefault()}
        <p className="text-danger">
          {gettext('An error occurred while creating the file.')}
          {' '}
          {interpolate(gettext('Error message: "%s".'), [downloadJob.error_summary])}
          {' '}
          {gettext('Please contact the maintainers of this site, if the problem persists.')}
        </p>
        </div>
      )
    default:
        return renderDefault()
    }
  }

  return (
    <div className="card mb-4">
      <div className="card-header">
        {gettext('Download table')}
      </div>
      <ul className="list-group list-group-flush">
        {
          downloadFormats && downloadFormats.map((downloadFormat, index) => {
            const downloadJob = downloadJobs?.filter((job) => job.key == 'table')
                                             .find((job) => job.format_key == downloadFormat.key)
            return (
            <li key={index} className="list-group-item">
              <div className="row">
                <div className="col-md-2">
                  <div>
                    {getDownloadJobInfo(downloadJob, downloadFormat)}
                  </div>
                </div>
                <div className="col-md-3">
                  {downloadFormat.label}
                </div>
                <div className="col-md-7">
                  {downloadFormat.help}
                </div>
              </div>
            </li>
          )}
          )
        }
      </ul>
    </div>
  )
}

TableDownload.propTypes = {
  jobId: PropTypes.string.isRequired,
  downloadJobs: PropTypes.array.isRequired,
  onSubmit: PropTypes.func.isRequired
}

export default TableDownload
