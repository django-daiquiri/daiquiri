import React from 'react'
import PropTypes from 'prop-types'

import Query from 'daiquiri/core/assets/js/components/Query'

import JobParameters from 'daiquiri/query/assets/js/components/query/job/JobParameters'

const ShowModal = ({ modal, job, loadForm, loadJob }) => {
  return (
    <div ref={modal.ref} className="modal" tabIndex="-1">
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{gettext('Query job')}</h5>
            <button type="button" className="btn-close" onClick={modal.hide}></button>
          </div>
          {
            job.id && (
              <div className="modal-body">
                <JobParameters job={job} />
                {
                  job.query && <>
                    <div className="modal-seperator mt-2"></div>
                    <dl className="row mb-0">
                      <dt className="col-sm-3 text-end">{gettext('Query')}</dt>
                      <dd className="col-sm-9 mb-0 ">
                        <div className="border border-light-subtle rounded ps-2 pe-2">
                          <Query query={job.query} />
                        </div>
                      </dd>
                    </dl>
                  </>
                }
              </div>
            )
          }
          <div className="modal-footer">
            <button type="button" className="btn btn-sm btn-secondary" onClick={() => {
              modal.hide()
              loadJob(job.id)
            }}>
              {gettext('Open the job in the query interface')}
            </button>
            <button type="button" className="btn btn-sm btn-secondary" onClick={() => {
              modal.hide()
              loadForm('sql', job.query)
            }}>
              {gettext('Open new query form with this query')}
            </button>
            <button type="button" className="btn btn-sm btn-secondary" onClick={modal.hide}>
              {gettext('Close')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

ShowModal.propTypes = {
  modal: PropTypes.object.isRequired,
  job: PropTypes.object.isRequired,
  loadForm: PropTypes.func.isRequired,
  loadJob: PropTypes.func.isRequired,
}

export default ShowModal
