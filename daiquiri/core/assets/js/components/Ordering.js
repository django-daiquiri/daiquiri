import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { isNil } from 'lodash'

const Ordering = ({ column, ordering, onOrder }) => {
  const asc = ordering == '-' + column.name
  const desc = ordering == column.name

  return !isNil(onOrder) && (
    <div className="ordering" onClick={() => onOrder(column)}>
      <div className={classNames('ordering-up bi bi-caret-up-fill', {
        'text-body-tertiary': !asc && !desc,
        'opacity-0': desc
      })}></div>
      <div className={classNames('ordering-down bi bi-caret-down-fill', {
        'text-body-tertiary': !asc && !desc,
        'opacity-0': asc
      })}></div>
    </div>
  )
}

Ordering.propTypes = {
  column: PropTypes.object.isRequired,
  ordering: PropTypes.string,
  onOrder: PropTypes.func,
}

export default Ordering
