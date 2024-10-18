import React from 'react'
import PropTypes from 'prop-types'

import { jobPhaseBadge } from 'daiquiri/query/assets/js/constants/job'

const JobParameters = ({ job }) => {
  return (
    <div className="job-parameters">
      <dl className="row mb-0">
        <dt className="col-sm-3 text-end">{gettext('Job status')}</dt>
        <dd className="col-sm-9 mb-0">
          <span className={jobPhaseBadge[job.phase]}>{job.phase_label}</span>
        </dd>

        {
          job.phase == 'ERROR' && (
            <>
              <dt className="col-sm-3 text-end">{gettext('Error')}</dt>
              <dd className="col-sm-9 text-danger mb-0">{job.error_summary}</dd>
            </>
          )
        }

        <dt className="col-sm-3 text-end">{gettext('Full database table name')}</dt>
        <dd className="col-sm-9 mb-0"><code>{job.schema_name}.{job.table_name}</code></dd>

        <dt className="col-sm-3 text-end">{gettext('Internal job id')}</dt>
        <dd className="col-sm-9 mb-0"><code>{job.id}</code></dd>

        <dt className="col-sm-3 text-end">{gettext('Time submitted')}</dt>
        <dd className="col-sm-9 mb-0">{job.creation_time_label}</dd>

        {
          job.queue && (
            <>
              <dt className="col-sm-3 text-end">{gettext('Queue')}</dt>
              <dd className="col-sm-9 mb-0">{job.queue}</dd>
            </>
          )
        }

        {
          job.start_time && job.creation_time && (
            <>
              <dt className="col-sm-3 text-end">{gettext('Time in queue')}</dt>
              <dd className="col-sm-9 mb-0">{job.time_queue} s</dd>
            </>
          )
        }

        {
          job.end_time && job.start_time && (
            <>
              <dt className="col-sm-3 text-end">{gettext('Time for query')}</dt>
              <dd className="col-sm-9 mb-0">{job.time_query} s</dd>
            </>
          )
        }

        {
          job.nrows !== null && (
            <>
              <dt className="col-sm-3 text-end">{gettext('Number of rows')}</dt>
              <dd className="col-sm-9 mb-0">{job.nrows}</dd>
            </>
          )
        }

        {
          job.size !== null && (
            <>
              <dt className="col-sm-3 text-end">{gettext('Size of the table')}</dt>
              <dd className="col-sm-9 mb-0">{job.size}</dd>
            </>
          )
        }

        {
          job.sources && job.sources.length > 0 && (
            <>
              <dt className="col-sm-3 text-end">{gettext('Source tables')}</dt>
              <dd className="col-sm-9 mb-0">
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
