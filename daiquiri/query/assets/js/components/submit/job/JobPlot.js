import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { jobPhaseClass, jobPhaseMessage } from 'daiquiri/query/assets/js/constants/job'
import { validTypes, excludedUcds } from 'daiquiri/query/assets/js/constants/plot'

import ColorScatter from './plots/ColorScatter'
import Histogram from './plots/Histogram'
import Scatter from './plots/Scatter'

import JobPlotType from './JobPlotType'

const JobPlot = ({ job, loadJob }) => {

  const [type, setType] = useState('scatter')
  const [columns, setColumns] = useState([])

  useEffect(() => setColumns(job.columns.filter((column) => (
    validTypes.includes(column.datatype) &&
    !excludedUcds.some((ucd) => (!isNil(column.ucd) && column.ucd.split(';').includes(ucd)))
  ))), [job])

  return job.phase == 'COMPLETED' ? (
    job.nrows > 1000000 ? (
      <h3>The plotting tool is available only for the query results with nrows fewer than 1M.</h3>
    ): (
    <div>
      <JobPlotType type={type} setType={setType} />
      {
        (type == 'scatter') && <Scatter job={job} columns={columns} loadJob={loadJob} />
      }
      {
        (type == 'colorScatter') && <ColorScatter job={job} columns={columns} />
      }
      {
        (type == 'histogram') && <Histogram job={job} columns={columns} />
      }
    </div>
    )
  ) : (
    <p className={jobPhaseClass[job.phase]}>{jobPhaseMessage[job.phase]}</p>
  )
}

JobPlot.propTypes = {
  job: PropTypes.object.isRequired,
  loadJob: PropTypes.func.isRequired,
}

export default JobPlot
