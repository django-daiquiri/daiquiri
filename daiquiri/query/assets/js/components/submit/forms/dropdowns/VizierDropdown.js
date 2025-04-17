import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { isEmpty } from 'lodash'

import { useVizierQuery } from 'daiquiri/query/assets/js/hooks/queries'

const VizierDropdown = ({ options, onClick }) => {
  const [searchValue, setSearchValue] = useState('')
  const [search, setSearch] = useState('')

  const { data: results } = useVizierQuery(options, search)

  return (
    <div className="mb-4">
      <div className="card">
        <div className="dq-browser">
          <div className="dq-browser-search">
            <div className="input-group">
              <input
                type="text"
                className="form-control"
                placeholder={gettext('Object name or coordinates')}
                value={searchValue}
                onChange={(event) => setSearchValue(event.target.value)}
                onKeyDown={(event) => {
                  if (event.code == 'Enter') {
                    setSearch(searchValue)
                  }
                }}>
              </input>
              <button className="btn btn-outline-primary" type="button" onClick={() => setSearch(searchValue)}>
                {gettext('Search on VizieR')}
              </button>
            </div>
          </div>
          <div className="dq-browser-table">
            <table className="table">
              <thead>
                <tr>
                  <th>{gettext('ID')}</th>
                  <th>{gettext('Coordinates')}</th>
                  <th>{gettext('Distance')}</th>
                  <th>{gettext('Catalog')}</th>
                </tr>
              </thead>
              {
                results && (
                  <tbody>
                    {
                      isEmpty(results.rows) ? (
                        !isEmpty(search) && (
                          <tr>
                            <td className="text-danger" colSpan="3">
                              {gettext('No results have been retrieved.')}
                            </td>
                          </tr>
                        )
                      ) : (
                        results.rows.map((row, index) => (
                          <tr key={index}>
                            <td>
                              <button
                                className="btn btn-link"
                                onClick={() => onClick('vizier', {query_string: row.id})}
                              >
                                {row.id}
                              </button>
                            </td>
                            <td>
                              <button
                                className="btn btn-link"
                                onClick={() => onClick('vizier', {query_string: row.ra})}
                              >
                                {row.ra}
                              </button>
                              {' '}
                              <button
                                className="btn btn-link"
                                onClick={() => onClick('vizier', {query_string: row.de})}
                              >
                                {row.de}
                              </button>
                            </td>
                            <td>
                              <button
                                className="btn btn-link"
                                onClick={() => onClick('vizier', {query_string: row.distance})}
                              >
                                {row.distance}
                              </button>
                            </td>
                            <td>{row.catalog}</td>
                          </tr>
                        ))
                      )
                    }
                  </tbody>
                )
              }
            </table>
          </div>
        </div>
      </div>
      <small className="form-text text-muted">
        {gettext('A click will paste a coordinate into the query field.')}
      </small>
    </div>
  )
}

VizierDropdown.propTypes = {
  options: PropTypes.object.isRequired,
  onClick: PropTypes.func.isRequired
}

export default VizierDropdown
