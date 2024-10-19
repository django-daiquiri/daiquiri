import React from 'react'
import PropTypes from 'prop-types'
import Plot from 'react-plotly.js'
import { isNil } from 'lodash'

import { config, layout } from 'daiquiri/query/assets/js/constants/plot'
import { getColumnLabel } from 'daiquiri/query/assets/js/utils/plot'

const ScatterPlot = ({ columns, values, x, y1, y2, y3  }) => {
  if (isNil(x)) {
    return null
  } else {
    const data = [[values.y1, y1], [values.y2, y2], [values.y3, y3]].reduce((data, [yValues, y]) => {
      if (isNil(y)) {
        return data
      } else {
        return [...data, {
          x: x,
          y: y,
          type: 'scattergl',
          mode: 'markers',
          marker: {
            color: yValues.color,
            symbol: yValues.symbol
          },
          name: yValues.column
        }]
      }
    }, [])

    const yLabel = [[values.y1, y1], [values.y2, y2], [values.y3, y3]].reduce((label, [yValues, y]) => {
      if (isNil(y)) {
        return label
      } else {
        return [...label, getColumnLabel(columns, yValues.column)]
      }
    }, []).join(', ')

    return (
      <div className="card">
        <div className="card-body">
          <div className="ratio ratio-16x9">
            <Plot
              data={data}
              layout={{
                ...layout,
                xaxis: {
                  title: {
                    text: getColumnLabel(columns, values.x.column),
                  },
                },
                yaxis: {
                  title: {
                    text: yLabel,
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

ScatterPlot.propTypes = {
  columns: PropTypes.array.isRequired,
  values: PropTypes.object.isRequired,
  x: PropTypes.array,
  y1: PropTypes.array,
  y2: PropTypes.array,
  y3: PropTypes.array
}

export default ScatterPlot
