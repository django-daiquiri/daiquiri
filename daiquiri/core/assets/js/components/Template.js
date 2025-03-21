import React from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

const Template = ({ template }) => {
  return !isNil(template) && (
    <span dangerouslySetInnerHTML={{ __html: template }} />
  )
}

Template.propTypes = {
  template: PropTypes.string
}

export default Template
