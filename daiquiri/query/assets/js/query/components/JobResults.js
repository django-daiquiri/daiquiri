import React, { useState } from 'react'
import PropTypes from 'prop-types'

import Table from '../../../../../core/assets/js/components/Table'

import { useJobColumnsQuery, useJobRowsQuery } from '../hooks/query'

const JobResults = ({ job }) => {
  const [params, setParams] = useState({
    page: 1,
    page_size: 10
  })

  const { data: columns } = useJobColumnsQuery(job.id, params)
  const { data: rows } = useJobRowsQuery(job.id, params)

  return (
    <Table
      columns={columns}
      rows={rows}
      params={params}
      setParams={setParams}
    />
  )
}

JobResults.propTypes = {
  job: PropTypes.object.isRequired
}

export default JobResults
