import React from 'react'
import PropTypes from 'prop-types'

import { useDownloadFormatsQuery } from 'daiquiri/query/assets/js/hooks/queries'

const TableDownload = ({ onSubmit }) => {
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

TableDownload.propTypes = {
  onSubmit: PropTypes.func.isRequired
}

export default TableDownload
