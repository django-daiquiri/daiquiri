import React from 'react'
import PropTypes from 'prop-types'

const Loading = ({ show }) => {
  return show && (
    <span>{gettext('Loading ...')}</span>
  )
}

Loading.defaultProps = {
  show: true
}

Loading.propTypes = {
  show: PropTypes.bool.isRequired
}

export default Loading
