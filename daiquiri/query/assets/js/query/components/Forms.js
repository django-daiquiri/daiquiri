import React from 'react'
import { isNil } from 'lodash'

import { useFormsQuery } from '../hooks/query'

const Forms = () => {
  const { data: forms } = useFormsQuery()

  return (
    <div className="card mb-3">
      <div className="card-header">
        {gettext('New query job')}
      </div>
      {
        isNil(forms) ? (
          <div className="card-body">
            <p>Loading ...</p>
          </div>
        ) : (
          <ul className="list-group list-group-flush">
            {
              forms.map((form) => (
                <li key={form.key} className="list-group-item">{form.key}</li>
              ))
            }
          </ul>
        )
      }
    </div>
  )
}

export default Forms
