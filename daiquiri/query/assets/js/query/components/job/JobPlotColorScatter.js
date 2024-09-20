import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { cmaps } from '../../constants/plot'
import { useJobPlotQuery } from '../../hooks/queries'

import JobPlotColorScatterForm from './JobPlotColorScatterForm'
import JobPlotColorScatterPlot from './JobPlotColorScatterPlot'

const JobPlotColorScatter = ({ jobId, columns }) => {

  const [values, setValues] = useState({
    x: {
      column: ''
    },
    y: {
      column: ''
    },
    z: {
      column: '',
      cmap: cmaps[0]
    }
  })

  useEffect(() => setValues({
    ...values,
    x: {
      ...values.x, column: isNil(columns[0]) ? '' : columns[0].name
    },
    y: {
      ...values.y, column: isNil(columns[1]) ? '' : columns[1].name
    },
    z: {
      ...values.z, column: isNil(columns[2]) ? '' : columns[2].name
    }
  }), [columns])

  const { data: x } = useJobPlotQuery(jobId, values.x.column)
  const { data: y } = useJobPlotQuery(jobId, values.y.column)
  const { data: z } = useJobPlotQuery(jobId, values.z.column)

  return (
    <div>
      <JobPlotColorScatterForm columns={columns} values={values} setValues={setValues} />
      <JobPlotColorScatterPlot columns={columns} values={values} x={x} y={y} z={z} />
    </div>
  )
}

JobPlotColorScatter.propTypes = {
  jobId: PropTypes.string.isRequired,
  columns: PropTypes.array.isRequired
}

export default JobPlotColorScatter
