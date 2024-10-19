import React from 'react'
import PropTypes from 'prop-types'
import Plot from 'react-plotly.js'
import { isNil } from 'lodash'

import { config, layout } from 'daiquiri/query/assets/js/constants/plot'
import { getColumnLabel } from 'daiquiri/query/assets/js/utils/plot'

const ColorScatterPlot = ({ columns, values, x, y, z  }) => {
  if (isNil(x) || isNil(y) || isNil(z)) {
    return null
  } else {
    return (
      <div className="card">
        <div className="card-body">
          <div className="ratio ratio-16x9">
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
                ...layout,
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

ColorScatterPlot.propTypes = {
  columns: PropTypes.array.isRequired,
  values: PropTypes.object.isRequired,
  x: PropTypes.array,
  y: PropTypes.array,
  z: PropTypes.array
}

export default ColorScatterPlot
