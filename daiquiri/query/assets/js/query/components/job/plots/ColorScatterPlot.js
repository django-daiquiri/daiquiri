import React from 'react'
import PropTypes from 'prop-types'
import Plot from 'react-plotly.js'
import { isNil } from 'lodash'

import { getColumnLabel } from '../../../utils/plot'

const ColorScatterPlot = ({ columns, values, x, y, z  }) => {
  if (isNil(x) || isNil(y) || isNil(z)) {
    return null
  } else {
    return (
      <div className="card">
        <div className="card-body">
          <div className="ratio ratio-1x1">
            <Plot
              data={[
                {
                  x: x,
                  y: y,
                  type: 'scattergl',
                  mode: 'markers',
                  marker: {
                    showscale: true,
                    color: z,
                    colorscale: values.z.cmap,
                    colorbar: {
                      title: {
                        text: getColumnLabel(columns, values.z.column),
                        side: 'right'
                      }
                    }
                  },
                }
              ]}
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
                    text: getColumnLabel(columns, values.y.column),
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

ColorScatterPlot.propTypes = {
  columns: PropTypes.array.isRequired,
  values: PropTypes.object.isRequired,
  x: PropTypes.array,
  y: PropTypes.array,
  z: PropTypes.array
}

export default ColorScatterPlot
