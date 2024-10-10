import React from 'react'
import PropTypes from 'prop-types'

import { useDownloadFormatsQuery } from '../../../hooks/queries'

const Table = ({ onSubmit }) => {
  const { data: downloadFormats } = useDownloadFormatsQuery()

  return (
    <div className="card mb-4">
      <div className="card-header">
        {gettext('Download table')}
      </div>
      <ul className="list-group list-group-flush">
        {
          downloadFormats && downloadFormats.map((downloadFormat, index) => (
            <li key={index} className="list-group-item">
              <div className="row">
                <div className="col-md-3">
                  <button className="btn btn-link text-start" onClick={() => onSubmit({
                    format_key: downloadFormat.key
                  })}>
                    {downloadFormat.label}
                  </button>
                </div>
                <div className="col-md-9">
                  {downloadFormat.help}
                </div>
              </div>
            </li>
          ))
        }
      </ul>
    </div>
  )
}

Table.propTypes = {
  onSubmit: PropTypes.func.isRequired
}

export default Table
