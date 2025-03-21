import React from 'react'
import PropTypes from 'prop-types'

const TableHandle = ({ columnIndex, widths, setWidths }) => {

  const handleResize = (mouseDownEvent) => {
    const initialSize = widths[columnIndex]
    const initialPosition = mouseDownEvent.pageX

    const onMouseMove = (mouseMoveEvent) => {
      const newWidths = initialSize - initialPosition + mouseMoveEvent.pageX
      setWidths(widths.map((width, index) => (columnIndex == index ? newWidths : width)))
    }

    const onMouseUp = () => {
      document.body.removeEventListener('mousemove', onMouseMove)
    }

    document.body.addEventListener('mousemove', onMouseMove)
    document.body.addEventListener('mouseup', onMouseUp, { once: true })
  }

  return (
    <div className="handle" onMouseDown={handleResize}>&nbsp;</div>
  )
}

TableHandle.propTypes = {
  columnIndex: PropTypes.number.isRequired,
  widths: PropTypes.array.isRequired,
  setWidths: PropTypes.func.isRequired
}

export default TableHandle
