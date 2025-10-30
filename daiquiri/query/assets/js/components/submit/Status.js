import React from 'react'
import { isNil, toInteger } from 'lodash'

import { baseUrl } from 'daiquiri/core/assets/js/utils/meta'
import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'
import Tooltip from 'daiquiri/core/assets/js/components/Tooltip'

import { useStatusQuery } from '../../hooks/queries'

const Status = () => {
  const { data: status } = useStatusQuery()

  const signupLink = `${baseUrl}/accounts/signup/`

  const size_percent = status ? (
    status.size > status.quota ? 100 : (toInteger(100 * (status.size / status.quota )))
  ) : 0

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
              status.guest && (
                <p dangerouslySetInnerHTML={{
                  __html: interpolate(gettext(
                    'You are currently using the guest account. For a personal account, please sign up <a href="%s")>here</a>'),
                    [signupLink]
                  )
                }} />
              )
            }
            {
              status.guest ? (
                <p>Using shared table space (Guest).</p>
              ) : (
                <p>Using personal table space.</p>
              )
            }
            <div className={status.size > status.quota ? 'text-danger': null}
              style={{ textAlign: 'right' }}
              dangerouslySetInnerHTML={{
              __html: interpolate(gettext(
                '%s / %s'),
                [bytes2human(status.size), bytes2human(status.quota)]
              )
            }} />
            <div className="progress" style={{ height: '1.3em' }}>
              <div className="progress-bar" role="progressbar"
                 style={{ width: size_percent + '%' }} aria-valuenow={size_percent} aria-valuemin="0" aria-valuemax="100">
              </div>
            </div>
            {
              status.size > status.quota && (
                <p className="text-danger">
                  {gettext('The Quota is exceeded. Please archive some jobs.')}
                </p>
              )
            }
            {status.max_active_jobs >0 &&(
              <div>
                <hr />
                <p>
                  <span className={status.active_jobs >= status.max_active_jobs ? 'text-danger' : ''}>
                    {interpolate(
                      gettext('Active Jobs: %s / %s   '),
                      [status.active_jobs, status.max_active_jobs]
                    )}
                  </span>{' '}
                   <Tooltip
                    tooltip={{
                      title: interpolate(
                        gettext(' Web Interface: %s <br/> TAP: %s'),
                        [status.active_jobs_interface, status.active_jobs_tap]
                      ),
                      placement: 'right',
                    }}>
                    <i className="bi bi-info-circle-fill"></i>
                  </Tooltip>
                </p>      
              </div>
            )}
          </div>
        )
      }
    </div>
  )
}

export default Status
