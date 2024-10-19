import React, { useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import { Popover as BootstrapPopover } from 'bootstrap'

const Popover = ({ children, title, content, placement }) => {
  const ref = useRef(null)

  useEffect(() => {
    if (title) {
      const t = new BootstrapPopover(ref.current, {
        title, content, placement, html: true, trigger: 'hover' })
      return () => t.dispose()
    }
  }, [title, placement])

  return React.cloneElement(children, { ref })
}

Popover.defaultProps = {
  placement: 'bottom'
}

Popover.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.string,
  content: PropTypes.string,
  placement: PropTypes.string,
}

export default Popover
