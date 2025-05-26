import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { colors, symbols } from 'daiquiri/query/assets/js/constants/plot'
import { useJobPlotQuery } from 'daiquiri/query/assets/js/hooks/queries'

import ScatterForm from './ScatterForm'
import ScatterPlot from './ScatterPlot'

const Scatter = ({ job, columns, loadJob }) => {

  const [values, setValues] = useState({
    x: {
      column: '',
    },
    y: {
      column: '',
      color: colors[0].hex,
      symbol: symbols[0].symbol
    }
  })

  useEffect(() => setValues({
    ...values,
    x: {
      ...values.x, column: isNil(columns[0]) ? '' : columns[0].name
    },
    y: {
      ...values.y, column: isNil(columns[1]) ? '' : columns[1].name
    }
  }), [columns])

  const { data: x } = useJobPlotQuery(job, values.x.column)
  const { data: y } = useJobPlotQuery(job, values.y.column)

  return (
    <div>
      <ScatterForm columns={columns} values={values} setValues={setValues} />
      { job && <ScatterPlot columns={columns} values={values} x={x} y={y} loadJob={loadJob} job={job}/>}
    </div>
  )
}

Scatter.propTypes = {
  job: PropTypes.object.isRequired,
  columns: PropTypes.array.isRequired,
  loadJob: PropTypes.func.isRequired,
}

export default Scatter
