import React from 'react'
import PropTypes from 'prop-types'

const JobResults = ({ job }) => {
  return <pre>Results {job.id}</pre>
}

JobResults.propTypes = {
  job: PropTypes.object.isRequired
}

export default JobResults
