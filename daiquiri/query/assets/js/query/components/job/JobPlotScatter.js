import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { colors, symbols } from '../../constants/plot'
import { useJobPlotQuery } from '../../hooks/queries'

import JobPlotScatterForm from './JobPlotScatterForm'
import JobPlotScatterPlot from './JobPlotScatterPlot'

const JobPlotScatter = ({ jobId, columns }) => {

  const [values, setValues] = useState({
    x: {
      column: '',
      label: ''
    },
    y1: {
      column: '',
      label: '',
      color: colors[0].hex,
      symbol: symbols[0].symbol
    },
    y2: {
      column: '',
      label: '',
      color: colors[1].hex,
      symbol: symbols[1].symbol
    },
    y3: {
      column: '',
      label: '',
      color: colors[2].hex,
      symbol: symbols[2].symbol
    }
  })

  useEffect(() => setValues({
    ...values,
    x: {
      ...values.x, column: isNil(columns[0]) ? '' : columns[0].name
    },
    y1: {
      ...values.y1, column: isNil(columns[1]) ? '' : columns[1].name
    }
  }), [columns])

  const { data: x } = useJobPlotQuery(jobId, values.x.column)
  const { data: y1 } = useJobPlotQuery(jobId, values.y1.column)
  const { data: y2 } = useJobPlotQuery(jobId, values.y2.column)
  const { data: y3 } = useJobPlotQuery(jobId, values.y3.column)

  return (
    <div>
      <JobPlotScatterForm columns={columns} values={values} setValues={setValues} />
      <JobPlotScatterPlot columns={columns} values={values} x={x} y1={y1} y2={y2} y3={y3} />
    </div>
  )
}

JobPlotScatter.propTypes = {
  jobId: PropTypes.string.isRequired,
  columns: PropTypes.array.isRequired
}

export default JobPlotScatter
