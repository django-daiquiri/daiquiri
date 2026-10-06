import React, { useEffect, useState } from 'react'
import PropTypes from 'prop-types'

import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'
import QueryApi from 'daiquiri/query/assets/js/api/QueryApi'
import { useDownloadFormatsQuery } from 'daiquiri/query/assets/js/hooks/queries'

import Tooltip  from 'daiquiri/core/assets/js/components/Tooltip'

const ACTIVE_DOWNLOAD_PHASES = ['QUEUED', 'PENDING', 'EXECUTING']

const TableDownload = ({ jobId, downloadJobs, onSubmit, onAbort, isSubmitting }) => {

  const { data: downloadFormats } = useDownloadFormatsQuery()
  const [selectedFormatKey, setSelectedFormatKey] = useState()

  useEffect(() => {
    if (downloadFormats?.length && !downloadFormats.some((format) => format.key == selectedFormatKey)) {
      setSelectedFormatKey(downloadFormats[0].key)
    }
  }, [downloadFormats, selectedFormatKey])

  const handleDownload = (downloadJob) => {
    window.location.href = QueryApi.getDownloadUrl(jobId, 'table', downloadJob.id)
  }

  const renderCancel = (downloadJob) => (
    <button type="button" className="btn btn-outline-danger w-100"
            onClick={() => onAbort('table', downloadJob.id)}>
      {gettext('Cancel')}
    </button>
  )

  const getDownloadStatus = (phase) => {
    switch (phase) {
    case 'QUEUED':
      return gettext('Queued..')
    case 'PENDING':
      return gettext('Pending..')
    default:
      return null
    }
  }

  const getDownloadJobInfo = (downloadJob, downloadFormat) => {
    const renderCreate = () => (
      <button type="button" className="btn btn-primary w-100"
              onClick={() => onSubmit({format_key: downloadFormat.key})}>
        <i className="bi bi-download"></i>&nbsp;
        {gettext('Download')}
      </button>
    )

    const renderDownload = () => (
      <button type="button" className="btn btn-primary w-100"
              onClick={() => handleDownload(downloadJob)}>
        <i className="bi bi-download"></i>&nbsp;
        {gettext('Download')}
      </button>
    )

    if (!downloadJob || !downloadJob.phase || downloadJob.phase == 'COMPLETED') {
      return downloadJob?.size > 0 ? renderDownload() : renderCreate()
    }

    if (ACTIVE_DOWNLOAD_PHASES.includes(downloadJob.phase)) {
      return renderCancel(downloadJob)
    }

    if (downloadJob.phase == 'ERROR') {
      return (
        <div>
          {renderCreate()}
          <p className="text-danger">
            {gettext('An error occurred while creating the file.')}
            {' '}
            {interpolate(gettext('Error message: "%s".'), [downloadJob.error_summary])}
            {' '}
            {gettext('Please contact the maintainers of this site, if the problem persists.')}
          </p>
        </div>
      )
    }

    return renderCreate()
  }

  const getDownloadJobStatus = (downloadJob) => {
    if (!downloadJob || !downloadJob.phase) {
      return null
    }

    if (downloadJob.phase == 'QUEUED' || downloadJob.phase == 'PENDING') {
      return (
        <span className="text-primary">
          <span className="spinner-border spinner-border-sm"></span>&nbsp;
          {getDownloadStatus(downloadJob.phase)}
        </span>
      )
    }

    if (downloadJob.phase == 'EXECUTING') {
      return (
        <span className="text-primary">
          <span className="spinner-border spinner-border-sm"></span>
          {downloadJob.size > 0 && ` ${bytes2human(downloadJob.size)}`}
        </span>
      )
    }

    return downloadJob.phase == 'COMPLETED' && downloadJob.size > 0 ? bytes2human(downloadJob.size) : null
  }

  const selectedFormat = downloadFormats?.find((format) => format.key == selectedFormatKey)
  const downloadJob = downloadJobs?.find(
    (job) => job.key == 'table' && job.format_key == selectedFormat?.key
  )
  const selectorDisabled = isSubmitting || (downloadJob && ACTIVE_DOWNLOAD_PHASES.includes(downloadJob.phase))

  return (
    <div className="card mb-4">
      <div className="card-header">
        {gettext('Download table')}
      </div>
      <div className="card-body">
        <div className="row align-items-center">
          <div className="col-md-2">
            {selectedFormat && getDownloadJobInfo(downloadJob, selectedFormat)}
          </div>
          <div className="col-md-4">
            {getDownloadJobStatus(downloadJob)}
          </div>
          <div className="col-md-6">
            <div className="d-flex align-items-center justify-content-end">
              <label htmlFor={`table-download-format-${jobId}`} className="form-label mb-0 me-2 text-nowrap">
                {gettext('Choose format:')}
              </label>
              <select
                id={`table-download-format-${jobId}`}
                className="form-select form-select-sm w-auto"
                value={selectedFormat?.key || ''}
                disabled={selectorDisabled}
                onChange={(event) => setSelectedFormatKey(event.target.value)}
              >
                {downloadFormats && downloadFormats.map((format) => (
                  <option key={format.key} value={format.key}>
                    .{format.extension}
                  </option>
                ))}
              </select>
              {selectedFormat && (
                <Tooltip tooltip={{ title: selectedFormat.help, placement: 'right' }}>
                  <i className="bi bi-info-circle-fill ms-2"></i>
                </Tooltip>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

TableDownload.propTypes = {
  jobId: PropTypes.string.isRequired,
  downloadJobs: PropTypes.array.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onAbort: PropTypes.func.isRequired,
  isSubmitting: PropTypes.bool.isRequired
}

export default TableDownload
