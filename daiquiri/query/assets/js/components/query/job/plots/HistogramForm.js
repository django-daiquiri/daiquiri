import React from 'react'
import PropTypes from 'prop-types'
import { useDebouncedCallback } from 'use-debounce'

import { operations } from 'daiquiri/query/assets/js/constants/plot'

const HistogramForm = ({ columns, values, setValues }) => {
  const setBins = useDebouncedCallback((event) => setValues({
    ...values, bins: event.target.value
  }), 500)
  const setSelectValue = useDebouncedCallback((event) => setValues({
    ...values, s: {...values.s, value: event.target.value}
  }), 500)

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
            <select className="form-select" id="scatter-plot-column" value={values.x.column} onChange={(event) => {
              setValues({...values, x: {...values.x, column: event.target.value}})
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
            <input type="number" className="form-control" defaultValue={values.bins} onChange={setBins} />
          </div>
        </div>
        <div className="row mt-1 align-items-center">
          <div className="col-2">
            <label htmlFor="scatter-plot-select" className="col-form-label">
              <strong>Selection</strong>
            </label>
          </div>
          <div className="col-4">
            <select className="form-select" id="scatter-plot-select" value={values.s.column} onChange={(event) => {
              setValues({...values, s: {...values.s, column: event.target.value}})
            }}>
              <option value="">---</option>
              {
                columns.map((column, columnIndex) => <option key={columnIndex} value={column.name}>{column.name}</option>)
              }
            </select>
          </div>
          <div className="col-2">
            <select className="form-select" value={values.s.operation} onChange={(event) => {
              setValues({...values, s: {...values.s, operation: event.target.value}})
            }}>
              {
                operations.map((operation, operationIndex) => <option key={operationIndex} value={operation.name}>{operation.name}</option>)
              }
            </select>
          </div>
          <div className="col-4">
            <input type="number" className="form-control" defaultValue={values.s.value} onChange={setSelectValue} />
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
