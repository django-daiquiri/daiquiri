import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { colors, symbols } from 'daiquiri/query/assets/js/constants/plot'
import { useJobPlotQuery } from 'daiquiri/query/assets/js/hooks/queries'

import ScatterForm from './ScatterForm'
import ScatterPlot from './ScatterPlot'

const Scatter = ({ job, columns, loadJob }) => {

  const [plotValues, setPlotValues] = useState({
    x: {
      column: '',
    },
    y: {
      column: '',
      color: colors[0].hex,
      symbol: symbols[0].symbol
    }
  })

  useEffect(() => setPlotValues({
    ...plotValues,
    x: {
      ...plotValues.x, column: isNil(columns[0]) ? '' : columns[0].name
    },
    y: {
      ...plotValues.y, column: isNil(columns[1]) ? '' : columns[1].name
    }
  }), [columns])

  const { data: x } = useJobPlotQuery(job, plotValues.x.column)
  const { data: y } = useJobPlotQuery(job, plotValues.y.column)

  return (
    <div>
      <ScatterForm columns={columns} plotValues={plotValues} setPlotValues={setPlotValues} />
      {job && <ScatterPlot columns={columns} plotValues={plotValues} x={x} y={y} loadJob={loadJob} job={job} />}
    </div>
  )
}

Scatter.propTypes = {
  job: PropTypes.object.isRequired,
  columns: PropTypes.array.isRequired,
  loadJob: PropTypes.func.isRequired,
}

export default Scatter
