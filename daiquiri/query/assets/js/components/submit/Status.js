import React from 'react'
import { isNil } from 'lodash'

import { baseUrl } from 'daiquiri/core/assets/js/utils/meta'
import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'

import { useStatusQuery } from '../../hooks/queries'

const Status = () => {
  const { data: status } = useStatusQuery()
  const signupLink = `${baseUrl}/accounts/signup/`

  return (
    <div className="card mb-3">
      <div className="card-header">
        {gettext('Database status')}
      </div>
      {
        isNil(status) ? (
          <div className="card-body">
            <p>Loading ...</p>
          </div>
        ) : (
          <div className="card-body">
            {
              status.queued_jobs && (
                <p>
                  {
                    interpolate(ngettext(
                      'There is one job in the queue.',
                      'There are %s jobs in the queue.',
                      status.queued_jobs
                    ), [status.queued_jobs])
                  }
                </p>
              )
            }
            {
              status.guest && (
                <p dangerouslySetInnerHTML={{
                  __html: interpolate(gettext(
                    'You are using the guest user. For a personal account, please sign up <a href="%s")>here</a>'),
                    [signupLink]
                  )
                }} />
              )
            }
            {
              status.guest ? (
                <p className={status.size > status.quota ? 'text-danger': null} dangerouslySetInnerHTML={{
                  __html: interpolate(gettext(
                    'The guest user is using %s of its quota of %s.'),
                    [bytes2human(status.size), bytes2human(status.quota)]
                  )
                }} />
              ) : (
                <p className={status.size > status.quota ? 'text-danger': null} dangerouslySetInnerHTML={{
                  __html: interpolate(gettext(
                    'You are using %s of your quota of %s.'),
                    [bytes2human(status.size), bytes2human(status.quota)]
                  )
                }} />
              )
            }
            {
              status.size > status.quota && (
                <p className="text-danger">
                  {gettext('The Quota is exceeded. Please remove some jobs.')}
                </p>
              )
            }
          </div>
        )
      }
    </div>
  )
}

export default Status
