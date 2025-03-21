import React from 'react'
import PropTypes from 'prop-types'

import { cmaps } from 'daiquiri/query/assets/js/constants/plot'

const ColorScatterForm = ({ columns, values, setValues }) => {
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
            <select className="form-select" id="scatter-plot-y-axis" value={values.y.column} onChange={(value) => {
              setValues({...values, y: {...values.y, column: value.target.value}})
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
            <select className="form-select" id="scatter-plot-z-axis" value={values.z.column} onChange={(value) => {
              setValues({...values, z: {...values.z, column: value.target.value}})
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
            <select className="form-select" id="scatter-plot-cmap" value={values.z.cmap} onChange={(value) => {
              setValues({...values, z: {...values.z, cmap: value.target.value}})
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
  values: PropTypes.object.isRequired,
  setValues: PropTypes.func.isRequired
}

export default ColorScatterForm
