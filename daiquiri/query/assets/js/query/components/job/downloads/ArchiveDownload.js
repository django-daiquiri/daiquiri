import React from 'react'
import PropTypes from 'prop-types'
import { isEmpty } from 'lodash'

import { isRefColumn, isImageColumn, isNoteColumn, isFileColumn} from 'daiquiri/core/assets/js/utils/table'

const ArchiveDownload = ({ columns, onSubmit }) => {

  const isArchiveColumn = (column) => isRefColumn(column) && (
    isImageColumn(column) || isNoteColumn(column) || isFileColumn(column)
  )

  const achiveColumns = columns.filter(column => isArchiveColumn(column))

  return !isEmpty(achiveColumns) && (
    <div className="card mb-4">
      <div className="card-header">
        {gettext('Download files')}
      </div>
      <ul className="list-group list-group-flush">
      {
        achiveColumns.map((column, columnIndex) => (
          <li key={columnIndex} className="list-group-item">
            <button className="btn btn-link"
                    onClick={() => onSubmit({column_name: column.name})}>
              {interpolate(gettext('Download all files in the column "%s" as a zip archive'), [column.name])}
            </button>
          </li>
        ))
      }
      </ul>
    </div>
  )
}

ArchiveDownload.propTypes = {
  columns: PropTypes.array.isRequired,
  onSubmit: PropTypes.func.isRequired
}

export default ArchiveDownload
