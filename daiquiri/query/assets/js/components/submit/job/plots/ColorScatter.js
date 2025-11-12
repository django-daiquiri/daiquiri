import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { cmaps } from 'daiquiri/query/assets/js/constants/plot'
import { useJobPlotQuery } from 'daiquiri/query/assets/js/hooks/queries'

import ColorScatterForm from './ColorScatterForm'
import ColorScatterPlot from './ColorScatterPlot'

const ColorScatter = ({ job, columns }) => {

  const [plotValues, setPlotValues] = useState({
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

  useEffect(() => setPlotValues({
    ...plotValues,
    x: {
      ...plotValues.x, column: isNil(columns[0]) ? '' : columns[0].name
    },
    y: {
      ...plotValues.y, column: isNil(columns[1]) ? '' : columns[1].name
    },
    z: {
      ...plotValues.z, column: isNil(columns[2]) ? '' : columns[2].name
    }
  }), [columns])

  const { data = []} = useJobPlotQuery(job, [plotValues.x.column, plotValues.y.column, plotValues.z.column]);
  const x = (data ?? []).map(row => row[0]);
  const y = (data ?? []).map(row => row[1]);
  const z = (data ?? []).map(row => row[2]);

  return (
    <div>
      <ColorScatterForm columns={columns} plotValues={plotValues} setPlotValues={setPlotValues} />
      <ColorScatterPlot columns={columns} plotValues={plotValues} x={x} y={y} z={z} />
    </div>
  )
}

ColorScatter.propTypes = {
  job: PropTypes.object.isRequired,
  columns: PropTypes.array.isRequired
}

export default ColorScatter
