import React from 'react'
import PropTypes from 'prop-types'

import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'
import { jobPhaseBadge } from 'daiquiri/query/assets/js/constants/job'

const JobParameters = ({ job }) => {
  return (
    <div className="job-parameters">

      <div className="row g-0 border rounded overflow-hidden text-center mb-4">
        <div className="col-6 col-md-3 border p-3">
          <div className="fw-bold">{gettext('Status')}</div>
            <span className={jobPhaseBadge[job.phase]}>{job.phase_label}</span>&nbsp;
            {
              job.result_status !== 'OK' ? (
                <span className="badge text-bg-warning">{job.result_status}</span>
              ) : ''
            }
        </div>

        <div className="col-6 col-md-3 border p-3">
          <div className="fw-bold">{gettext('Rows')}</div>
          <div className="fs-5">
            {job.nrows !== null ? (job.nrows) : '-'}
          </div>
        </div>

        <div className="col-6 col-md-3 border p-3">
          <div className="fw-bold">{gettext('Result size')}</div>
          <div className="fs-5">
          { job.size !== null ? bytes2human(job.size) : '-' }
          </div>
        </div>

        <div className="col-6 col-md-3 border p-3">
          <div className="fw-bold">{gettext('Query time')}</div>
          <div className="fs-5">
          { (job.start_time !== null && job.end_time !== null) ? `${job.time_query.toFixed(1)} s` : '-' }
          </div>
        </div>
      </div>

      <dl className="row mb-0">
        {
          job.phase == 'ERROR' && (
            <>
              <dt className="col-md-3 text-md-end">{gettext('Error')}</dt>
              <dd className="col-md-9 text-danger mb-0">{job.error_summary}</dd>
            </>
          )
        }

        <dt className="col-md-3 text-md-end">{gettext('Table name')}</dt>
        <dd className="col-md-9 mb-0"><code className="text-primary">{job.schema_name}.{job.table_name}</code></dd>

        <dt className="col-md-3 text-md-end">{gettext('Time submitted')}</dt>
        <dd className="col-md-9 mb-0">{job.creation_time_label}</dd>

        {
          job.queue && (
            <>
              <dt className="col-md-3 text-md-end">{gettext('Selected queue')}</dt>
              <dd className="col-md-9 mb-0">{job.queue}</dd>
            </>
          )
        }

        {
          job.start_time && job.creation_time && (
            <>
              <dt className="col-md-3 text-md-end">{gettext('Time in queue')}</dt>
              <dd className="col-md-9 mb-0">{job.time_queue.toFixed(1)} s</dd>
            </>
          )
        }

        {
          job.end_time && job.start_time && (
            <>
              <dt className="col-md-3 text-md-end">{gettext('Time for query')}</dt>
              <dd className="col-md-9 mb-0">{job.time_query.toFixed(1)} s</dd>
            </>
          )
        }

        {
          job.sources && job.sources.length > 0 && (
            <>
              <dt className="col-md-3 text-md-end">{gettext('Source tables')}</dt>
              <dd className="col-md-9 mb-0">
              {
                job.sources.map((source, sourceIndex) => (
                  <a key={sourceIndex} className="d-inline-block" href={source.url} target="_blank">
                    {source.schema_name}.{source.table_name}
                  </a>
                ))
              }
              </dd>
            </>
          )
        }

        <dt className="col-md-3 text-md-end">{gettext('Internal job id')}</dt>
        <dd className="col-md-9 mb-0"><code className="text-secondary">{job.id}</code></dd>

      </dl>
    </div>
  )
}

JobParameters.propTypes = {
  job: PropTypes.object.isRequired,
}

export default JobParameters
