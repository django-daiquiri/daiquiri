import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { validTypes, excludedUcds } from '../../constants/plot'

import JobPlotScatter from './JobPlotScatter'
import JobPlotType from './JobPlotType'

const JobPlot = ({ job }) => {

  const [type, setType] = useState('scatter')
  const [columns, setColumns] = useState([])

  useEffect(() => setColumns(job.columns.filter((column) => (
    validTypes.includes(column.datatype) &&
    !excludedUcds.some((ucd) => (!isNil(column.ucd) && column.ucd.split(';').includes(ucd)))
  ))), [job])

  return (
    <div>
      <JobPlotType type={type} setType={setType} />
      {
        (type == 'scatter') && <JobPlotScatter jobId={job.id} columns={columns} />
      }
    </div>
  )
}

JobPlot.propTypes = {
  job: PropTypes.object.isRequired
}

export default JobPlot
