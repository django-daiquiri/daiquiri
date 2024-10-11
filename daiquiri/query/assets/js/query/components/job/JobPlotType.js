import React from 'react'
import PropTypes from 'prop-types'

const types = [
  ['scatter', 'Scatter plot'],
  ['colorScatter', 'Scatter plot (color coded)'],
  ['histogram', 'Histogram'],
]


const JobPlotType = ({ type, setType }) => {
  return (
    <div className="card mb-2">
      <div className="card-body">
        {
          types.map(([value, label]) => (
            <div key={value} className="form-check form-check-inline">
              <input className="form-check-input" type="radio" name="jobType" id={`job-type-${value}`} value={value}
                     checked={type == value} onChange={() => setType(value)}/>
              <label className="form-check-label" htmlFor={`job-type-${value}`}>{label}</label>
            </div>
          ))
        }
      </div>
    </div>
  )
}

JobPlotType.propTypes = {
  type: PropTypes.string.isRequired,
  setType: PropTypes.func.isRequired
}

export default JobPlotType
