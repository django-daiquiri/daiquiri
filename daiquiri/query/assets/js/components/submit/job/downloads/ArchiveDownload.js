import React from 'react'
import PropTypes from 'prop-types'
import { isEmpty } from 'lodash'

import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'
import { isRefColumn, isImageColumn, isNoteColumn, isFileColumn} from 'daiquiri/core/assets/js/utils/table'

const ArchiveDownload = ({ jobId, columns, downloadJobs, onSubmit }) => {

  const isArchiveColumn = (column) => isRefColumn(column) && (
    isImageColumn(column) || isNoteColumn(column) || isFileColumn(column)
  )

  const archiveColumns = columns.filter(column => isArchiveColumn(column))

  const handleDownload = (downloadJob) => {
    const url = `/query/api/jobs/${jobId}/download/archive/${downloadJob.id}/?download=true`
    window.location.href = url
  }

  const getDownloadJobInfo = (downloadJob, column) => {
    const renderDefault = () => (
      <a className="btn btn-link"
              onClick={() => onSubmit({column_name: column.name})}>
        <i className="bi bi-file-zip"></i>&nbsp;
        {interpolate(gettext('Create a zip archive for all files in the column "%s".'), [column.name])}
      </a>
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
              {gettext('Queued..')}
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
          <p className="text-primary">
            <span>
            <span className="spinner-border spinner-border-sm">
            </span>
              {gettext(' Creating.. ')}
              {interpolate(gettext('(%s).'), [bytes2human(downloadJob.size)])}
            </span>
          </p>
        </div>
      )
    case 'COMPLETED':
      return downloadJob.size > 0 ? (
          <button className="btn btn-link text-start"
                  onClick={() => handleDownload(downloadJob)}>
            <i className="bi bi-download"></i>&nbsp;
            {interpolate(gettext(' .zip (%s) Download all files in the column "%s".'), [bytes2human(downloadJob.size), column.name])}
          </button>
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
          {gettext('Please contact the maintainers of this site, if the problem persists.')}
        </p>
        </div>
      )
    default:
        return renderDefault()
    }
  }

  return !isEmpty(archiveColumns) && (
    <div className="card mb-4">
      <div className="card-header">
        {gettext('Download files')}
      </div>
      <ul className="list-group list-group-flush">
      {
        archiveColumns.map((column, columnIndex) => {
          const downloadJob = downloadJobs?.filter((job) => job.key == 'archive')
                                           .find((job) => job.column_name == column.name)
          return (
          <li key={columnIndex} className="list-group-item">
            {getDownloadJobInfo(downloadJob, column)}
          </li>
          )
        })
      }
      </ul>
    </div>
  )
}

ArchiveDownload.propTypes = {
  jobId: PropTypes.string.isRequired,
  columns: PropTypes.array.isRequired,
  downloadJobs: PropTypes.array.isRequired,
  onSubmit: PropTypes.func.isRequired
}

export default ArchiveDownload

/*
          <a className="btn btn-link text-start"
                  href={getDownloadUrl(downloadJob)}>
            <i className="bi bi-download"></i>&nbsp;
            {interpolate(gettext(' .zip (%s) Download all files in the column "%s".'), [bytes2human(downloadJob.size), column.name])}
          </a>
*/
