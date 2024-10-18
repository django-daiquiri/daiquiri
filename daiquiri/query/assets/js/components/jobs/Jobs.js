import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { useModal } from 'daiquiri/core/assets/js/hooks/modal'

import { jobPhaseBadge } from 'daiquiri/query/assets/js/constants/job'
import { useJobsQuery } from 'daiquiri/query/assets/js/hooks/queries'

import List from 'daiquiri/core/assets/js/components/list/List'

import AbortModal from 'daiquiri/query/assets/js/components/modals/AbortModal'
import ArchiveModal from 'daiquiri/query/assets/js/components/modals/ArchiveModal'
import RenameModal from 'daiquiri/query/assets/js/components/modals/RenameModal'
import ShowModal from 'daiquiri/query/assets/js/components/modals/ShowModal'

const Jobs = ({ loadForm, loadJob }) => {
  const initalParams = {
    ordering: '-creation_time'
  }

  const [params, setParams] = useState(initalParams)
  const [modalJob, setModalJob] = useState({})

  const showModal = useModal()
  const abortModal = useModal()
  const archiveModal = useModal()
  const renameModal = useModal()

  const { data, fetchNextPage, hasNextPage } = useJobsQuery(params)
  const count = isNil(data) ? null : interpolate(ngettext(
    'One job found.', '%s jobs found', data.pages[0].count
  ), [data.pages[0].count])
  const rows = isNil(data) ? [] : data.pages.reduce((messages, page) => {
    return [...messages, ...page.results]
  }, [])

  const handleOrdering = (column) => {
    const ordering = (params.ordering == column.name) ? '-' + column.name : column.name
    setParams({ ...params, ordering })
  }

  const handleModal = (modal, job) => {
    setModalJob(job)
    modal.show()
  }

  const handleSearch = (search) => {
    setParams({ ...params, search })
  }

  const handleReset = () => {
    setParams(initalParams)
  }

  const columns = [
    {
      name: 'id', label: gettext('ID'), width: '30%', onOrder: handleOrdering, formatter: (job) => (
        <button className="btn btn-link" onClick={() => handleModal(showModal, job)}>{job.id}</button>
      )
    },
    {
      name: 'run_id', label: gettext('Run ID'), width: '10%', onOrder: handleOrdering
    },
    {
      name: 'table_name', label: gettext('Table'), width: '20%', onOrder: handleOrdering
    },
    {
      name: 'creation_time', label: gettext('Created'), width: '20%', onOrder: handleOrdering, formatter: (job) => (
        <span>{job.creation_time_label}</span>
      )
    },
    {
      name: 'phase', label: gettext('Phase'), width: '10%', onOrder: handleOrdering, formatter: (job) => (
        <span className={jobPhaseBadge[job.phase]}>{job.phase_label}</span>
      )
    },
    {
      width: '10%', formatter: (job) => (
        <span className="d-flex gap-1 flex-wrap justify-content-end">
          <button className="btn btn-link" title={gettext('Show job details')}
                  onClick={() => handleModal(showModal, job)}>
            <span className="material-symbols-rounded">visibility</span>
          </button>
          <button className="btn btn-link" title={gettext('Open the job in the query interface')}
                  onClick={() => loadJob(job.id)}>
            <span className="material-symbols-rounded">exit_to_app</span>
          </button>
          {
            job.phase == 'COMPLETED' && (
              <button className="btn btn-link" title={gettext('Update job')}
                      onClick={() => handleModal(renameModal, job)}>
                <span className="material-symbols-rounded">edit</span>
              </button>
            )
          }
          <button className="btn btn-link" title={gettext('Open new query form with this query')}
                  onClick={() => loadForm('sql', job.query)}>
            <span className="material-symbols-rounded">refresh</span>
          </button>
          {
            ['EXECUTING', 'PENDING', 'QUEUED'].includes(job.phase) && (
              <button className="btn btn-link" title={gettext('Abort job')}
                      onClick={() => handleModal(abortModal, job)}>
                <span className="material-symbols-rounded">cancel</span>
              </button>
            )
          }
          {
            !['EXECUTING', 'PENDING', 'QUEUED', 'ARCHIVED'].includes(job.phase) && (
              <button className="btn btn-link" title={gettext('Archive job')}
                      onClick={() => handleModal(archiveModal, job)}>
                <span className="material-symbols-rounded">delete</span>
              </button>
            )
          }
        </span>
      )
    }
  ]

  const buttons = [
    {
      label: gettext('Back to query'),
      onClick: () => loadForm('sql')
    }
  ]

  return (
    <div>
      <h1 className="mb-4">Query jobs</h1>

      <List
        columns={columns}
        rows={rows}
        ordering={params.ordering}
        count={count}
        onSearch={handleSearch}
        onNext={hasNextPage ? fetchNextPage : null}
        onReset={handleReset}
        buttons={buttons}
        checkboxes={{}}
      />

      <ShowModal modal={showModal} job={modalJob} loadForm={loadForm} loadJob={loadJob} />
      <RenameModal modal={renameModal} job={modalJob} />
      <AbortModal modal={abortModal} job={modalJob} />
      <ArchiveModal modal={archiveModal} job={modalJob} />
    </div>
  )
}

Jobs.propTypes = {
  loadForm: PropTypes.func.isRequired,
  loadJob: PropTypes.func.isRequired
}

export default Jobs
