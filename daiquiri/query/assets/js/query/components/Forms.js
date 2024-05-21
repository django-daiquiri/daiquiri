import React from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { useFormsQuery } from '../hooks/query'
import { basePath } from '../utils/location'

import Loading from './Loading'

const Forms = ({ loadForm }) => {
  const { data: forms } = useFormsQuery()

  const handleLoadForm = (event, form) => {
    event.preventDefault()
    loadForm(form.key)
  }

  return (
    <div className="card mb-3">
      <div className="card-header">
        {gettext('New query job')}
      </div>
      {
        isNil(forms) ? (
          <div className="card-body">
            <Loading />
          </div>
        ) : (
          <ul className="list-group list-group-flush">
            {
              forms.map((form) => (
                <li key={form.key} className="list-group-item">
                  <a href={`${basePath}/${form.key}/`} onClick={(event) => handleLoadForm(event, form)}>
                    {form.key}
                  </a>
                </li>
              ))
            }
          </ul>
        )
      }
    </div>
  )
}

Forms.propTypes = {
  loadForm: PropTypes.func.isRequired
}

export default Forms
