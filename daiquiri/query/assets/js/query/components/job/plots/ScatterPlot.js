import React from 'react'
import PropTypes from 'prop-types'
import Plot from 'react-plotly.js'
import { isNil } from 'lodash'

import { getColumnLabel } from '../../../utils/plot'

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
          <div className="ratio ratio-1x1">
            <Plot
              data={data}
              layout={{
                autosize: true,
                aspectratio: 1,
                dragmode: 'pan',
                margin: {
                  l: 40,
                  r: 40,
                  b: 40,
                  t: 40
                },
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
              style={{
                width: '100%',
              }}
              useResizeHandler={true}
              config={{
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['select2d', 'lasso2d']
              }}
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
