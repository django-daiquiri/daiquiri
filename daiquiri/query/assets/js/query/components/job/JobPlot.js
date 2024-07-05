import React from 'react'
import PropTypes from 'prop-types'

const JobPlot = ({ job }) => {
  return <pre>Plot {job.id}</pre>
}

JobPlot.propTypes = {
  job: PropTypes.object.isRequired
}

export default JobPlot
