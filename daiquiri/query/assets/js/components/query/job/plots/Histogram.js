import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { operations } from 'daiquiri/query/assets/js/constants/plot'
import { useJobPlotQuery } from 'daiquiri/query/assets/js/hooks/queries'

import HistogramForm from './HistogramForm'
import HistogramPlot from './HistogramPlot'

const Histogram = ({ job, columns }) => {

  const [values, setValues] = useState({
    x: {
      column: ''
    },
    s: {
      column: '',
      operation: operations[0].name,
      value: 0
    },
    bins: 20,
  })

  useEffect(() => setValues({
    ...values,
    x: {
      ...values.x, column: isNil(columns[0]) ? '' : columns[0].name
    }
  }), [columns])

  const { data: x } = useJobPlotQuery(job, values.x.column)
  const { data: s } = useJobPlotQuery(job, values.s.column)

  return (
    <div>
      <HistogramForm columns={columns} values={values} setValues={setValues} />
      <HistogramPlot columns={columns} values={values} x={x} s={s} />
    </div>
  )
}

Histogram.propTypes = {
  job: PropTypes.object.isRequired,
  columns: PropTypes.array.isRequired
}

export default Histogram
