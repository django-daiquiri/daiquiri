import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { cmaps } from 'daiquiri/query/assets/js/constants/plot'
import { useJobPlotQuery } from 'daiquiri/query/assets/js/hooks/queries'

import ColorScatterForm from './ColorScatterForm'
import ColorScatterPlot from './ColorScatterPlot'

const ColorScatter = ({ job, columns }) => {

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

  const { data: x } = useJobPlotQuery(job, values.x.column)
  const { data: y } = useJobPlotQuery(job, values.y.column)
  const { data: z } = useJobPlotQuery(job, values.z.column)

  return (
    <div>
      <ColorScatterForm columns={columns} values={values} setValues={setValues} />
      <ColorScatterPlot columns={columns} values={values} x={x} y={y} z={z} />
    </div>
  )
}

ColorScatter.propTypes = {
  job: PropTypes.object.isRequired,
  columns: PropTypes.array.isRequired
}

export default ColorScatter
