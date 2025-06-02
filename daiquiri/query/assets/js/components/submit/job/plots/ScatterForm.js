import React from 'react'
import PropTypes from 'prop-types'

import { colors, symbols } from 'daiquiri/query/assets/js/constants/plot'

const ScatterForm = ({ columns, plotValues, setPlotValues }) => {

  const getSymbolHtml = (symbol) => {
    const s = symbols.find(s => s.symbol == symbol)
    return (
      <i className={s.icon}></i>
    )
  }

  return (
    <div className="card mb-2">
      <div className="card-body">
        <div className="row align-items-center">
          <div className="col-2">
            <label htmlFor="scatter-plot-x-axis" className="col-form-label">
              <strong>X axis</strong>
            </label>
          </div>
          <div className="col-4">
            <select className="form-select" id="scatter-plot-x-axis" value={plotValues.x.column} onChange={(value) => {
              setPlotValues({ ...plotValues, x: { ...plotValues.x, column: value.target.value } })
            }}>
              <option value="">---</option>
              {
                columns.map((column, columnIndex) => <option key={columnIndex} value={column.name}>{column.name}</option>)
              }
            </select>
          </div>
        </div>
        {
          <div key="y" className="row mt-1 align-items-center">
            <div className="col-2">
              <label htmlFor={`scatter-plot-y-axis`} className="col-form-label">
                <strong>Y axis</strong>
              </label>
            </div>
            <div className="col-4">
              <select className="form-select" id="scatter-plot-y-axis" value={plotValues.y.column} onChange={(value) => {
                setPlotValues({ ...plotValues, y: { ...plotValues.y, column: value.target.value } })
              }}>
                <option value="">---</option>
                {
                  columns.map((column, columnIndex) => <option key={columnIndex} value={column.name}>{column.name}</option>)
                }
              </select>
            </div>
            <div className="col-1">
              <div className="query-plot-color-symbol text-center" style={{ color: plotValues.y.color }}>{getSymbolHtml(plotValues.y.symbol)}</div>
            </div>
            <div className="col-2">
              <select className="form-select" id="scatter-plot-y-color" value={plotValues.y.color} onChange={(value) => {
                setPlotValues({ ...plotValues, y: { ...plotValues.y, color: value.target.value } })
              }}>
                {
                  colors.map(color => <option key={color.hex} value={color.hex}>{color.name}</option>)
                }
              </select>
            </div>
            <div className="col-3">
              <select className="form-select" id="scatter-plot-y-symbol" value={plotValues.y.symbol} onChange={(value) => {
                setPlotValues({ ...plotValues, y: { ...plotValues.y, symbol: value.target.value } })
              }}>
                {
                  symbols.map(symbol => <option key={symbol.symbol} value={symbol.symbol}>{symbol.name}</option>)
                }
              </select>
            </div>
          </div>
        }
      </div>
    </div>
  )
}

ScatterForm.propTypes = {
  columns: PropTypes.array.isRequired,
  plotValues: PropTypes.object.isRequired,
  setPlotValues: PropTypes.func.isRequired
}

export default ScatterForm
