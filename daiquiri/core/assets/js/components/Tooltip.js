import React, { useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import { Tooltip as BootstrapTooltip } from 'bootstrap'

const Tooltip = ({ children, title, placement }) => {
  const ref = useRef(null)

  useEffect(() => {
    if (title) {
      const t = new BootstrapTooltip(ref.current, {
        title, placement, html: true, trigger: 'hover' })
      return () => t.dispose()
    }
  }, [title, placement])

  return React.cloneElement(children, { ref })
}

Tooltip.defaultProps = {
  placement: 'bottom'
}

Tooltip.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.string,
  placement: PropTypes.string,
}

export default Tooltip
