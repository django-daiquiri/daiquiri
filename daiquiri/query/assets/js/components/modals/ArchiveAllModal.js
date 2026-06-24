import React, { useState } from 'react'
import PropTypes from 'prop-types'

import { useArchiveAllJobsMutation } from 'daiquiri/query/assets/js/hooks/mutations'

const ArchiveAllModal = ({ modal, jobs, onComplete }) => {
  const mutation = useArchiveAllJobsMutation()

  const [isRunning, setIsRunning] = useState(false)
  const [processed, setProcessed] = useState(0)

  const progress =
    jobs.length === 0 ? 0 : Math.round((processed / jobs.length) * 100)

  const handleSubmit = async () => {
    if (!jobs.length) return

    setIsRunning(true)
    setProcessed(0)

    try {
      for (const job of jobs) {
        await mutation.mutateAsync(job)
        setProcessed(prev => prev + 1)
      }

      onComplete?.()
      modal.hide()
    } finally {
      setIsRunning(false)
    }
  }

  const handleClose = () => {
    if (isRunning) return
    setProcessed(0)
    modal.hide()
  }

  return (
    <div ref={modal.ref} className="modal" tabIndex="-1">
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{gettext('Archive job')}</h5>
            <button type="button" className="btn-close" onClick={handleClose} disabled={isRunning} />
          </div>
          <div className="modal-body">
            <p dangerouslySetInnerHTML={{
              __html: interpolate(
                gettext('You are about to archive all <code>%s</code> query jobs.'), 
                [jobs.length]
              )
            }} />
            <p className="text-danger">
              {gettext('This action cannot be undone!')}
            </p>
            {isRunning && (
              <>
                <p dangerouslySetInnerHTML={{
                  __html: interpolate(
                  gettext('%s of %s jobs archived'),
                    [processed, jobs.length]
                  )
                }}
                />
                <div className="progress">
                  <div className="progress-bar" role="progressbar" style={{ width: `${progress}%` }} aria-valuenow={progress} aria-valuemin="0" aria-valuemax="100">
                    {progress}%
                  </div>
                </div>
              </>
            )}
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-sm btn-secondary" onClick={handleClose} disabled={isRunning}>
              {gettext('Close')}
            </button>
            <button
              type="button" className="btn btn-sm btn-danger" onClick={handleSubmit} disabled={isRunning || jobs.length === 0}>
              {isRunning
                ? gettext('Archiving...')
                : gettext('Archive')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

ArchiveAllModal.propTypes = {
  modal: PropTypes.object.isRequired,
  jobs: PropTypes.array.isRequired,
  onComplete: PropTypes.func
}

export default ArchiveAllModal