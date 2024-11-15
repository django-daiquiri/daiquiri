import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { useModal } from 'daiquiri/core/assets/js/hooks/modal'

import { jobPhases, jobPhaseBadge } from 'daiquiri/query/assets/js/constants/job'
import { useJobsQuery } from 'daiquiri/query/assets/js/hooks/queries'

import Checkbox from 'daiquiri/core/assets/js/components/form/Checkbox'
import List from 'daiquiri/core/assets/js/components/list/List'

import AbortModal from 'daiquiri/query/assets/js/components/modals/AbortModal'
import ArchiveModal from 'daiquiri/query/assets/js/components/modals/ArchiveModal'
import RenameModal from 'daiquiri/query/assets/js/components/modals/RenameModal'
import ShowModal from 'daiquiri/query/assets/js/components/modals/ShowModal'

const Jobs = ({ loadForm, loadJob }) => {
  const initialParams = {
    ordering: '-creation_time',
    phase: Object.keys(jobPhases).filter(key => key != 'ARCHIVED')
  }

  const [params, setParams] = useState(initialParams)
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

  const handleModal = (modal, job) => {
    setModalJob(job)
    modal.show()
  }

  const handleSearch = (search) => {
    setParams({ ...params, search })
  }

  const handleReset = () => {
    setParams(initialParams)
  }

  const handleFilter = (phase) => {
    setParams({ ...params,
      phase: params.phase.includes(phase) ? params.phase.filter(p => p != phase) : [ ...params.phase, phase ]
    })
  }

  const handleOrdering = (column) => {
    const ordering = (params.ordering == column.name) ? '-' + column.name : column.name
    setParams({ ...params, ordering })
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
            <i className="bi bi-eye"></i>
          </button>
          <button className="btn btn-link" title={gettext('Open the job in the query interface')}
                  onClick={() => loadJob(job.id)}>
            <i className="bi bi-box-arrow-in-right"></i>
          </button>
          {
            job.phase == 'COMPLETED' && (
              <button className="btn btn-link" title={gettext('Update job')}
                      onClick={() => handleModal(renameModal, job)}>
                <i className="bi bi-pencil"></i>
              </button>
            )
          }
          <button className="btn btn-link" title={gettext('Open new query form with this query')}
                  onClick={() => loadForm('sql', job.query, job.query_language)}>
            <i className="bi bi-play-circle"></i>
          </button>
          {
            ['EXECUTING', 'PENDING', 'QUEUED'].includes(job.phase) && (
              <button className="btn btn-link" title={gettext('Abort job')}
                      onClick={() => handleModal(abortModal, job)}>
                <i className="bi bi-x-circle"></i>
              </button>
            )
          }
          {
            !['EXECUTING', 'PENDING', 'QUEUED', 'ARCHIVED'].includes(job.phase) && (
              <button className="btn btn-link" title={gettext('Archive job')}
                      onClick={() => handleModal(archiveModal, job)}>
                <i className="bi bi-trash"></i>
              </button>
            )
          }
        </span>
      )
    }
  ]

  const headerButtons = [
    {
      label: gettext('New query'),
      onClick: () => loadForm('sql')
    }
  ]

  const headerChildren = (
    <div className="d-md-flex flex-wrap gap-3">
      {
        Object.entries(jobPhases).map(([phase, phaseLabel], phaseIndex) => (
          <Checkbox
            key={phaseIndex}
            label={phaseLabel}
            checked={params.phase.includes(phase)}
            onChange={() => handleFilter(phase)}
          />
        ))
      }
    </div>
  )

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
        headerButtons={headerButtons}
        headerChildren={headerChildren}
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
