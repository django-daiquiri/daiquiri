import React from 'react'
import PropTypes from 'prop-types'

import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'
import { jobPhaseBadge } from 'daiquiri/query/assets/js/constants/job'

const JobParameters = ({ job }) => {
  return (
    <div className="job-parameters">
      <dl className="row mb-0">
        <dt className="col-md-3 text-md-end">{gettext('Job status')}</dt>
        <dd className="col-md-9 mb-0">
          <span className={jobPhaseBadge[job.phase]}>{job.phase_label}</span>&nbsp;
          {
            job.result_status !== 'OK' ? (
              <span className="badge text-bg-warning">{job.result_status}</span>
            ) : ''
          }
        </dd>

        {
          job.phase == 'ERROR' && (
            <>
              <dt className="col-md-3 text-md-end">{gettext('Error')}</dt>
              <dd className="col-md-9 text-danger mb-0">{job.error_summary}</dd>
            </>
          )
        }

        <dt className="col-md-3 text-md-end">{gettext('Full database table name')}</dt>
        <dd className="col-md-9 mb-0"><code>{job.schema_name}.{job.table_name}</code></dd>

        <dt className="col-md-3 text-md-end">{gettext('Internal job id')}</dt>
        <dd className="col-md-9 mb-0"><code>{job.id}</code></dd>

        <dt className="col-md-3 text-md-end">{gettext('Time submitted')}</dt>
        <dd className="col-md-9 mb-0">{job.creation_time_label}</dd>

        {
          job.queue && (
            <>
              <dt className="col-md-3 text-md-end">{gettext('Queue')}</dt>
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
          job.nrows !== null && (
            <>
              <dt className="col-md-3 text-md-end">{gettext('Number of rows')}</dt>
            <dd className="col-md-9 mb-0">{job.nrows}{job.result_status !== 'OK' ? (` (${job.result_status})` ) : ''}</dd>
            </>
          )
        }

        {
          job.size !== null && (
            <>
              <dt className="col-md-3 text-md-end">{gettext('Size of the table')}</dt>
              <dd className="col-md-9 mb-0">{bytes2human(job.size)}</dd>
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
                  <a key={sourceIndex} className="d-inline-block" href={source.url} target="blank">
                    {source.schema_name}.{source.table_name}
                  </a>
                ))
              }
              </dd>
            </>
          )
        }
      </dl>
    </div>
  )
}

JobParameters.propTypes = {
  job: PropTypes.object.isRequired,
}

export default JobParameters
