import React, { useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import { Tooltip as BootstrapTooltip } from 'bootstrap'

const Tooltip = ({ children, tooltip }) => {
  const ref = useRef(null)

  useEffect(() => {
    if (tooltip && tooltip.title) {
      const t = new BootstrapTooltip(ref.current, {
        html: true, trigger: 'hover', placement: 'bottom', ...tooltip
      })
      return () => t.dispose()
    }
  }, [tooltip])

  return React.cloneElement(children, { ref })
}

Tooltip.propTypes = {
  children: PropTypes.node.isRequired,
  tooltip: PropTypes.object,
}

export default Tooltip
