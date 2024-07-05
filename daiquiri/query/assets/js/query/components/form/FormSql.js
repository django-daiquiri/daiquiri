import React from 'react'
import PropTypes from 'prop-types'

import { useLsState } from 'daiquiri/core/assets/js/hooks/ls'

import Template from 'daiquiri/core/assets/js/components/Template'

import { useQueryLanguagesQuery, useQueuesQuery } from '../../hooks/query'

const FormSql = ({ form }) => {

  const { data: queryLanguages } = useQueryLanguagesQuery()
  const { data: queues } = useQueuesQuery()

  const [openDropdown, setOpenDropdown] = useLsState('query.openDropdown')

  const handleDrowpdown = (dropdownKey) => {
    setOpenDropdown(openDropdown == dropdownKey ? false : dropdownKey)
  }

  const handleSubmit = () => {
    console.log('handleSubmit')
  }

  const handleClear = () => {
    console.log('handleClear')
  }

  return (
    <div className="form">
      <h2>{form.label}</h2>
      <Template template={form.template} />

      <div className="sql-dropdowns">
        <div className="d-flex">
          <button type="button" className="btn btn-outline-secondary dropdown-toggle me-2"
                  onClick={() => handleDrowpdown('schemas')}>
            {gettext('Database')}
          </button>
          <button type="button" className="btn btn-outline-secondary dropdown-toggle me-2"
                  onClick={() => handleDrowpdown('columns')}>
            {gettext('Columns')}
          </button>
          <button type="button" className="btn btn-outline-secondary dropdown-toggle me-2"
                  onClick={() => handleDrowpdown('functions')}>
            {gettext('Functions')}
          </button>
          <button type="button" className="btn btn-outline-secondary dropdown-toggle me-2"
                  onClick={() => handleDrowpdown('simbad')}>
            {gettext('Simbad')}
          </button>
          <button type="button" className="btn btn-outline-secondary dropdown-toggle me-auto"
                  onClick={() => handleDrowpdown('vizier')}>
            {gettext('VizieR')}
          </button>
          <button type="button" className="btn btn-outline-secondary dropdown-toggle"
                  onClick={() => handleDrowpdown('examples')}>
            {gettext('Examples')}
          </button>
        </div>

        {
          openDropdown && (
            <div className="card mt-2">
              <div className="card-body">
                {openDropdown}
              </div>
            </div>
          )
        }
      </div>

      <div className="sql-form mt-3">
        <div className="mb-3">
          <label htmlFor="input" className="form-label">{gettext('SQL query')}</label>
          <textarea className="form-control" id="sql-input" rows="12"></textarea>
        </div>

        <div className="row">
          <div className="col-md-4">
            <label htmlFor="table-name" className="form-label">{gettext('Table name')}</label>
            <input type="text" className="form-control" id="table-name"></input>
          </div>
          <div className="col-md-2">
            <label htmlFor="table-name" className="form-label">{gettext('Run id')}</label>
            <input type="text" className="form-control" id="table-name"></input>
          </div>
          <div className="col-md-3">
            <label htmlFor="query-languages" className="form-label">{gettext('Query language')}</label>
            <select id="query-languages" className="form-select">
            {
              queryLanguages && queryLanguages.map((ql) => <option key={ql.id} value={ql.id}>{ql.text}</option>)
            }
            </select>
          </div>
          <div className="col-md-3">
            <label htmlFor="queue" className="form-label">{gettext('Queue')}</label>
            <select id="queue" className="form-select">
            {
              queues && queues.map((q) => <option key={q.id} value={q.id}>{q.text}</option>)
            }
            </select>
          </div>
        </div>

        <div className="d-flex mt-4">
          <button type="button" className="btn btn-primary me-auto" onClick={() => handleSubmit()}>
            {gettext('Submit new SQL Query')}
          </button>
          <button type="button" className="btn btn-outline-secondary" onClick={() => handleClear()}>
            {gettext('Clear input window')}
          </button>
        </div>
      </div>
    </div>
  )
}

FormSql.propTypes = {
  form: PropTypes.object.isRequired
}

export default FormSql
