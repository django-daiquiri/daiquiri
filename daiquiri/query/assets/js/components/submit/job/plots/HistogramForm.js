import React from 'react'
import PropTypes from 'prop-types'
import { useDebouncedCallback } from 'use-debounce'

import { operations } from 'daiquiri/query/assets/js/constants/plot'

const HistogramForm = ({ columns, plotValues, setPlotValues }) => {
  const setBins = useDebouncedCallback((event) => setPlotValues({
    ...plotValues, bins: event.target.value
  }), 500)
  const setSelectValue = useDebouncedCallback((event) => setPlotValues({
    ...plotValues, s: { ...plotValues.s, value: event.target.value }
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
            <select className="form-select" id="scatter-plot-column" value={plotValues.x.column} onChange={(event) => {
              setPlotValues({ ...plotValues, x: { ...plotValues.x, column: event.target.value } })
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
            <input type="number" className="form-control" defaultValue={plotValues.bins} onChange={setBins} />
          </div>
        </div>
        <div className="row mt-1 align-items-center">
          <div className="col-2">
            <label htmlFor="scatter-plot-select" className="col-form-label">
              <strong>Selection</strong>
            </label>
          </div>
          <div className="col-4">
            <select className="form-select" id="scatter-plot-select" value={plotValues.s.column} onChange={(event) => {
              setPlotValues({ ...plotValues, s: { ...plotValues.s, column: event.target.value } })
            }}>
              <option value="">---</option>
              {
                columns.map((column, columnIndex) => <option key={columnIndex} value={column.name}>{column.name}</option>)
              }
            </select>
          </div>
          <div className="col-2">
            <select className="form-select" value={plotValues.s.operation} onChange={(event) => {
              setPlotValues({ ...plotValues, s: { ...plotValues.s, operation: event.target.value } })
            }}>
              {
                operations.map((operation, operationIndex) => <option key={operationIndex} value={operation.name}>{operation.name}</option>)
              }
            </select>
          </div>
          <div className="col-4">
            <input type="number" className="form-control" defaultValue={plotValues.s.value} onChange={setSelectValue} />
          </div>
        </div>
      </div>
    </div>
  )
}

HistogramForm.propTypes = {
  columns: PropTypes.array.isRequired,
  plotValues: PropTypes.object.isRequired,
  setPlotValues: PropTypes.func.isRequired
}

export default HistogramForm
