import React from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

const ListFooter = ({ onNext }) => {
  return (
    <div className="dq-list-footer d-md-flex justify-content-center">
      {
        !isNil(onNext) && (
          <ul className="pagination">
            <li className="page-item">
              <span className="page-link" onClick={onNext}>
                {gettext('Load more')}
              </span>
            </li>
          </ul>
        )
      }
    </div>
  )
}

ListFooter.propTypes = {
  onNext: PropTypes.func,
}

export default ListFooter
