import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { isEmpty } from 'lodash'

import { useSimbadQuery } from 'daiquiri/query/assets/js/hooks/queries'

const SimbadDropdown = ({ options, onClick }) => {
  const [searchValue, setSearchValue] = useState('')
  const [search, setSearch] = useState('')

  const { data: results } = useSimbadQuery(options, search)

  return (
    <div className="mb-4">
      <div className="card">
        <div className="dq-browser">
          <div className="dq-browser-search">
            <div className="input-group">
              <input
                type="text"
                className="form-control"
                placeholder={gettext('Object name')}
                value={searchValue}
                onChange={(event) => setSearchValue(event.target.value)}
                onKeyDown={(event) => {
                  if (event.code == 'Enter') {
                    setSearch(searchValue)
                  }
                }}>
              </input>
              <button className="btn btn-outline-primary" type="button" onClick={() => setSearch(searchValue)}>
                {gettext('Search on SIMBAD')}
              </button>
            </div>
          </div>
          <div className="dq-browser-table">
            <table className="table">
              <thead>
                <tr>
                  <th>{gettext('Object')}</th>
                  <th>{gettext('Type')}</th>
                  <th>{gettext('Coordinates')}</th>
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
                            <td>{row.object}</td>
                            <td>{row.type}</td>
                            <td>
                              <button className="btn btn-link" onClick={() => onClick('simbad', {query_string: row.ra})}>
                                {row.ra}
                              </button>
                              {' '}
                              <button className="btn btn-link" onClick={() => onClick('simbad', {query_string: row.de})}>
                                {row.de}
                              </button>
                            </td>
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

SimbadDropdown.propTypes = {
  options: PropTypes.object.isRequired,
  onClick: PropTypes.func.isRequired
}

export default SimbadDropdown
