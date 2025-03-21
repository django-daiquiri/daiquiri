import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { isNil } from 'lodash'

import { useFormsQuery } from '../../hooks/queries'
import { basePath } from '../../utils/location'

import Loading from 'daiquiri/core/assets/js/components/Loading'

const FormList = ({ formKey, loadForm }) => {
  const { data: forms } = useFormsQuery()

  const handleLoadForm = (event, form) => {
    event.preventDefault()
    loadForm(form.key)
  }

  return (
    <div className="card card-nav mb-3">
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
                <li key={form.key} className={classNames({'list-group-item': true, 'active': form.key === formKey})}>
                  <a href={`${basePath}/${form.key}/`} onClick={(event) => handleLoadForm(event, form)}>
                    {form.label}
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

FormList.propTypes = {
  formKey: PropTypes.string,
  loadForm: PropTypes.func.isRequired
}

export default FormList
