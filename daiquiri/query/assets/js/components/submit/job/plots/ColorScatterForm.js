import React from 'react'
import PropTypes from 'prop-types'

import { cmaps } from 'daiquiri/query/assets/js/constants/plot'

const ColorScatterForm = ({ columns, plotValues, setPlotValues }) => {
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
        <div className="row mt-1 align-items-center">
          <div className="col-2">
            <label htmlFor="scatter-plot-y-axis" className="col-form-label">
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
        </div>
        <div className="row mt-1 align-items-center">
          <div className="col-2">
            <label htmlFor="scatter-plot-z-axis" className="col-form-label">
              <strong>Z axis</strong>
            </label>
          </div>
          <div className="col-4">
            <select className="form-select" id="scatter-plot-z-axis" value={plotValues.z.column} onChange={(value) => {
              setPlotValues({ ...plotValues, z: { ...plotValues.z, column: value.target.value } })
            }}>
              <option value="">---</option>
              {
                columns.map((column, columnIndex) => <option key={columnIndex} value={column.name}>{column.name}</option>)
              }
            </select>
          </div>
          <div className="col-2">
            <label htmlFor="scatter-plot-cmap" className="col-form-label">
              <strong>Colormap</strong>
            </label>
          </div>
          <div className="col-4">
            <select className="form-select" id="scatter-plot-cmap" value={plotValues.z.cmap} onChange={(value) => {
              setPlotValues({ ...plotValues, z: { ...plotValues.z, cmap: value.target.value } })
            }}>
              {
                cmaps.map((cmap, cmapIndex) => <option key={cmapIndex} value={cmap}>{cmap}</option>)
              }
            </select>
          </div>
        </div>
      </div>
    </div>
  )
}

ColorScatterForm.propTypes = {
  columns: PropTypes.array.isRequired,
  plotValues: PropTypes.object.isRequired,
  setPlotValues: PropTypes.func.isRequired
}

export default ColorScatterForm
