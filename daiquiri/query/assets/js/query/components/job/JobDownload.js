import React from 'react'
import PropTypes from 'prop-types'

const JobDownload = ({ job }) => {
  return <pre>Download {job.id}</pre>
}

JobDownload.propTypes = {
  job: PropTypes.object.isRequired
}

export default JobDownload
