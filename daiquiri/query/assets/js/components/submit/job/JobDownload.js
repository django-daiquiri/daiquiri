import React, { useEffect, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import { isNil, isEmpty } from 'lodash'

import { downloadFile } from 'daiquiri/core/assets/js/utils/api'
import QueryApi from 'daiquiri/query/assets/js/api/QueryApi'
import { jobPhaseClass, jobPhaseMessage } from 'daiquiri/query/assets/js/constants/job'
import { useSubmittedDownloadsQuery, useDownloadFormsQuery } from 'daiquiri/query/assets/js/hooks/queries'
import {
  useAbortDownloadJobMutation,
  useSubmitDownloadJobMutation
} from 'daiquiri/query/assets/js/hooks/mutations'

import ArchiveDownload from './downloads/ArchiveDownload'
import FormDownload from './downloads/FormDownload'
import TableDownload from './downloads/TableDownload'

const ACTIVE_DOWNLOAD_PHASES = ['QUEUED', 'PENDING', 'EXECUTING']

const JobDownload = ({ job }) => {

  const mutation = useSubmitDownloadJobMutation()
  const abortMutation = useAbortDownloadJobMutation()
  const requestSequence = useRef(0)
  const pollingTimeout = useRef()
  const [pollingInterval, setPollingInterval] = useState(3000)
  const [latestDownload, setLatestDownload] = useState(null)
  const [requestedDownloads, setRequestedDownloads] = useState([])
  const [pendingRequests, setPendingRequests] = useState(0)
  const [submittingDownloadKey, setSubmittingDownloadKey] = useState(null)
  const downloadedSequence = useRef(null)

  const { data: downloadForms } = useDownloadFormsQuery(job.id)

  const { data: downloadJobs } = useSubmittedDownloadsQuery(job.id, pollingInterval) || []

  const startFastPolling = () => {
    clearTimeout(pollingTimeout.current)
    setPollingInterval(1000)
    pollingTimeout.current = setTimeout(() => setPollingInterval(3000), 5000)
  }

  const handleSubmit = (downloadKey, data) => {
    const sequence = ++requestSequence.current
    startFastPolling()
    setLatestDownload(null)
    setPendingRequests((current) => current + 1)
    setSubmittingDownloadKey(downloadKey)

    mutation.mutate({
      job,
      downloadKey,
      data,
      onSuccess: (download) => {
        setRequestedDownloads((current) => current.includes(download.id) ? current : [...current, download.id])
        if (sequence == requestSequence.current) {
          setLatestDownload({...download, sequence})
        }
      },
      onSettled: () => {
        setPendingRequests((current) => current - 1)
        setSubmittingDownloadKey((current) => current == downloadKey ? null : current)
      }
    })
  }

  const handleAbort = (downloadKey, downloadJobId) => {
    abortMutation.mutate({
      job,
      downloadKey,
      downloadJobId,
      onSuccess: () => {
        if (latestDownload?.id == downloadJobId) {
          setLatestDownload(null)
        }
      }
    })
  }

  useEffect(() => {
    if (!latestDownload || downloadedSequence.current == latestDownload.sequence) return

    const downloadJob = downloadJobs?.find((download) => download.id == latestDownload.id)
    if (downloadJob?.phase == 'COMPLETED' && downloadJob.size > 0) {
      downloadedSequence.current = latestDownload.sequence
      downloadFile(QueryApi.getDownloadUrl(job.id, latestDownload.key, latestDownload.id))
    }
  }, [downloadJobs, job.id, latestDownload])

  useEffect(() => {
    if (pollingInterval != 1000 || pendingRequests || !requestedDownloads.length) return

    const allDownloadsFinished = requestedDownloads.every((downloadId) => {
      const download = downloadJobs?.find((item) => item.id == downloadId)
      return download && !ACTIVE_DOWNLOAD_PHASES.includes(download.phase)
    })

    if (allDownloadsFinished) {
      clearTimeout(pollingTimeout.current)
      setPollingInterval(3000)
    }
  }, [downloadJobs, pendingRequests, pollingInterval, requestedDownloads])

  useEffect(() => {
    return () => clearTimeout(pollingTimeout.current)
  }, [])

  return job.phase == 'COMPLETED' ? (
    <div className="query-download">
      <p className="mb-4">
        {
          isEmpty(downloadForms) ? gettext('The download of the results is currently not available.') :
          gettext('For further processing of the data, you can create a file from the results table' +
                 ' and then download it to your local machine. For this file several formats are available.' +
                 ' Please choose a format from the selector below.')
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
                onAbort={handleAbort}
                isSubmitting={submittingDownloadKey == 'table'}
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
                onAbort={handleAbort}
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
