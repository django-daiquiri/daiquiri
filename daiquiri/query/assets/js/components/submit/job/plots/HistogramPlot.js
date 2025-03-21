import React from 'react'
import PropTypes from 'prop-types'
import Plot from 'react-plotly.js'
import { isNil } from 'lodash'

import { config, layout, operations } from 'daiquiri/query/assets/js/constants/plot'
import { getColumnLabel } from 'daiquiri/query/assets/js/utils/plot'

const HistogramPlot = ({ columns, values, x, s }) => {
  if (isNil(x)) {
    return null
  } else {
    const data = [
      {
        x: x,
        type: 'histogram',
        nbinsx: values.bins
      }
    ]

    if (!isNil(s)) {
      const operation = operations.find(operation => operation.name == values.s.operation) || operations[0]

      data.push({
        x: x.filter((value, index) => operation.operation(s[index], values.s.value)),
        type: 'histogram',
        nbinsx: values.bins
      })
    }

    return (
      <div className="card">
        <div className="card-body">
          <div className="ratio ratio-16x9">
            <Plot
              data={data}
              layout={{
                ...layout,
                bargap: 0.1,
                xaxis: {
                  title: {
                    text: getColumnLabel(columns, values.x.column),
                  },
                },
                yaxis: {
                  title: {
                    text: 'Count',
                  }
                }
              }}
              style={{width: '100%'}}
              useResizeHandler={true}
              config={config}
            />
          </div>
        </div>
      </div>
    )
  }
}

HistogramPlot.propTypes = {
  columns: PropTypes.array.isRequired,
  values: PropTypes.object.isRequired,
  x: PropTypes.array,
  s: PropTypes.array,
}

export default HistogramPlot
