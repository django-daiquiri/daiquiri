import React from 'react'
import PropTypes from 'prop-types'

import { colors, symbols } from '../../constants/plot'

const JobPlotScatterForm = ({ columns, values, setValues }) => {

  const labels = {
    y1: <span>Y<sub>1</sub></span>,
    y2: <span>Y<sub>2</sub></span>,
    y3: <span>Y<sub>3</sub></span>
  }

  const getSymbolHtml = (symbol) => {
    const s = symbols.find(s => s.symbol == symbol)
    return (
      <span className="material-symbols-rounded" style={{ fontSize: s.fontSize }}>{s.materialSymbol}</span>
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
            <select className="form-select" id="scatter-plot-x-axis" value={values.x.column} onChange={(value) => {
              setValues({...values, x: {...values.x, column: value.target.value}})
            }}>
              <option>---</option>
              {
                columns.map((column, columnIndex) => <option key={columnIndex} value={column.name}>{column.name}</option>)
              }
            </select>
          </div>
        </div>
        {
          ['y1', 'y2', 'y3'].map(y => (
            <div key={y} className="row mt-1 align-items-center">
              <div className="col-2">
                <label htmlFor={`scatter-plot-${y}-axis`} className="col-form-label">
                  <strong>{labels[y]} axis</strong>
                </label>
              </div>
              <div className="col-4">
                <select className="form-select" id={`scatter-plot-${y}-axis`} value={values[y].column} onChange={(value) => {
                  setValues({...values, [y]: {...values[y], column: value.target.value}})
                }}>
                  <option>---</option>
                  {
                    columns.map((column, columnIndex) => <option key={columnIndex} value={column.name}>{column.name}</option>)
                  }
                </select>
              </div>
              <div className="col-1">
                <div className="query-plot-color-symbol text-center" style={{color: values[y].color}}>{getSymbolHtml(values[y].symbol)}</div>
              </div>
              <div className="col-2">
                <select className="form-select" id={`scatter-plot-${y}-color`} value={values[y].color} onChange={(value) => {
                  setValues({...values, [y]: {...values[y], color: value.target.value}})
                }}>
                  {
                    colors.map(color => <option key={color.hex} value={color.hex}>{color.name}</option>)
                  }
                </select>
              </div>
              <div className="col-3">
                <select className="form-select" id={`scatter-plot-${y}-symbol`} value={values[y].symbol} onChange={(value) => {
                  setValues({...values, [y]: {...values[y], symbol: value.target.value}})
                }}>
                  {
                    symbols.map(symbol => <option key={symbol.symbol} value={symbol.symbol}>{symbol.label}</option>)
                  }
                </select>
              </div>
            </div>
          ))
        }
      </div>
    </div>
  )
}

JobPlotScatterForm.propTypes = {
  columns: PropTypes.array.isRequired,
  values: PropTypes.object.isRequired,
  setValues: PropTypes.func.isRequired
}

export default JobPlotScatterForm