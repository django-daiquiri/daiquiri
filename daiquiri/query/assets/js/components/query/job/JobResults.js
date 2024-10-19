import React, { useState } from 'react'
import PropTypes from 'prop-types'

import { jobPhaseClass, jobPhaseMessage } from 'daiquiri/query/assets/js/constants/job'
import { useJobColumnsQuery, useJobRowsQuery } from 'daiquiri/query/assets/js/hooks/queries'

import Table from 'daiquiri/core/assets/js/components/table/Table'

const JobResults = ({ job }) => {
  const [params, setParams] = useState({
    page: 1,
    page_size: 10
  })

  const { data: columns } = useJobColumnsQuery(job, params)
  const { data: rows } = useJobRowsQuery(job, params)

  return job.phase == 'COMPLETED' ? (
    <Table
      columns={columns}
      rows={rows}
      params={params}
      setParams={setParams}
    />
  )  : (
    <p className={jobPhaseClass[job.phase]}>{jobPhaseMessage[job.phase]}</p>
  )
}

JobResults.propTypes = {
  job: PropTypes.object.isRequired
}

export default JobResults
