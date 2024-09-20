import React from 'react'
import PropTypes from 'prop-types'

import { operations } from '../../../constants/plot'

const HistogramForm = ({ columns, values, setValues }) => {

  return (
    <div className="card mb-2">
      <div className="card-body">
        <div className="row align-items-center">
          <div className="col-2">
            <label htmlFor="scatter-plot-column" className="col-form-label">
              <strong>Column</strong>
            </label>
          </div>
          <div className="col-4">
            <select className="form-select" id="scatter-plot-column" value={values.x.column} onChange={(value) => {
              setValues({...values, x: {...values.x, column: value.target.value}})
            }}>
              <option>---</option>
              {
                columns.map((column, columnIndex) => <option key={columnIndex} value={column.name}>{column.name}</option>)
              }
            </select>
          </div>
        </div>
        <div className="row mt-1 align-items-center">
          <div className="col-2">
            <label htmlFor="scatter-plot-column" className="col-form-label">
              <strong>Bins</strong>
            </label>
          </div>
          <div className="col-4">
            <input type="number" className="form-control" value={values.bins} onChange={(value) => {
              setValues({...values, bins: value.target.value})
            }} />
          </div>
        </div>
        <div className="row mt-1 align-items-center">
          <div className="col-2">
            <label htmlFor="scatter-plot-select" className="col-form-label">
              <strong>Selection</strong>
            </label>
          </div>
          <div className="col-4">
            <select className="form-select" id="scatter-plot-select" value={values.s.column} onChange={(value) => {
              setValues({...values, s: {...values.s, column: value.target.value}})
            }}>
              <option>---</option>
              {
                columns.map((column, columnIndex) => <option key={columnIndex} value={column.name}>{column.name}</option>)
              }
            </select>
          </div>
          <div className="col-2">
            <select className="form-select" value={values.s.operation} onChange={(value) => {
              setValues({...values, s: {...values.s, operation: value.target.value}})
            }}>
              <option>---</option>
              {
                operations.map((operation, operationIndex) => <option key={operationIndex} value={operation.name}>{operation.name}</option>)
              }
            </select>
          </div>
          <div className="col-4">
            <input type="number" className="form-control" value={values.s.value} onChange={(value) => {
              setValues({...values, s: {...values.s, value: value.target.value}})
            }} />
          </div>
        </div>
      </div>
    </div>
  )
}

HistogramForm.propTypes = {
  columns: PropTypes.array.isRequired,
  values: PropTypes.object.isRequired,
  setValues: PropTypes.func.isRequired
}

export default HistogramForm
