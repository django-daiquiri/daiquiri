import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { colors, symbols } from 'daiquiri/query/assets/js/constants/plot'
import { useJobPlotQuery } from 'daiquiri/query/assets/js/hooks/queries'

import ScatterForm from './ScatterForm'
import ScatterPlot from './ScatterPlot'

const Scatter = ({ job, columns }) => {

  const [values, setValues] = useState({
    x: {
      column: '',
    },
    y1: {
      column: '',
      color: colors[0].hex,
      symbol: symbols[0].symbol
    },
    y2: {
      column: '',
      color: colors[1].hex,
      symbol: symbols[1].symbol
    },
    y3: {
      column: '',
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

  const { data: x } = useJobPlotQuery(job, values.x.column)
  const { data: y1 } = useJobPlotQuery(job, values.y1.column)
  const { data: y2 } = useJobPlotQuery(job, values.y2.column)
  const { data: y3 } = useJobPlotQuery(job, values.y3.column)

  return (
    <div>
      <ScatterForm columns={columns} values={values} setValues={setValues} />
      <ScatterPlot columns={columns} values={values} x={x} y1={y1} y2={y2} y3={y3} />
    </div>
  )
}

Scatter.propTypes = {
  job: PropTypes.object.isRequired,
  columns: PropTypes.array.isRequired
}

export default Scatter
