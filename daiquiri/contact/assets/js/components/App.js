import React, { useState } from 'react'
import { isNil, omit } from 'lodash'

import { useModal } from 'daiquiri/core/assets/js/hooks/modal'

import { useMessagesQuery } from '../hooks/queries'
import { useUpdateMessageMutation } from '../hooks/mutations'
import { messageStatus, messageStatusBadge } from '../constants/messages'

import Checkbox from 'daiquiri/core/assets/js/components/form/Checkbox'
import List from 'daiquiri/core/assets/js/components/list/List'

import Modal from './Modal.js'

const App = () => {
  const initalParams = {}

  const [params, setParams] = useState(initalParams)

  const modal = useModal()
  const [modalMessage, setModalMessage] = useState({})

  const mutation = useUpdateMessageMutation()

  const { data, fetchNextPage, hasNextPage } = useMessagesQuery(params)
  const count = isNil(data) ? null : interpolate(ngettext(
    'One contact message found.', '%s contact messages found', data.pages[0].count
  ), [data.pages[0].count])
  const rows = isNil(data) ? [] : data.pages.reduce((messages, page) => {
    return [...messages, ...page.results]
  }, [])

  const handleModal = (message) => {
    setModalMessage(message)
    modal.show()
  }

  const handleSearch = (search) => {
    setParams({ ...params, search })
  }

  const handleNext = () => {
    if (hasNextPage) {
      fetchNextPage()
    }
  }

  const handleReset = () => {
    setParams(initalParams)
  }

  const handleFilter = (status) => {
    setParams((params.status == status) ? omit(params, ['status']) : {...params, status})
  }

  const handleOrdering = (column) => {
    const ordering = (params.ordering == column.name) ? '-' + column.name : column.name
    setParams({ ...params, ordering })
  }

  const handleUpdate = (message, status) => {
    mutation.mutate({ message: {...message, status }})
  }

  const columns = [
    {
      name: 'id', label: gettext('ID'), width: '5%'
    },
    {
      name: 'subject', label: gettext('Subject'), width: '15%', onOrder: handleOrdering, formatter: (message) => (
        <button className="btn btn-link" onClick={() => handleModal(message)}>{message.subject}</button>
      )
    },
    {
      name: 'author', label: gettext('Author'), onOrder: handleOrdering,  width: '15%' },
    {
      name: 'email', label: gettext('Email'), onOrder: handleOrdering,  width: '15%', formatter: (message) => (
        <a href={message.mailto}>{message.email}</a>
      )
    },
    {
      name: 'created', label: gettext('Created'), onOrder: handleOrdering,  width: '20%', formatter: (message) => (
        message.created_label
      )
    },
    {
      name: 'status', label: gettext('Status'), onOrder: handleOrdering,  width: '15%', formatter: (message) => (
        <span className={messageStatusBadge[message.status]}>{message.status_label}</span>
      )
    },
    {
      width: '10%', formatter: (message) => (
        <span className="d-flex gap-1 justify-content-end">
          <a href={message.mailto} className="material-symbols-rounded">reply</a>
          <button className="btn btn-link" onClick={() => handleModal(message)}>
            <span className="material-symbols-rounded">visibility</span>
          </button>
          {
            message.status == 'ACTIVE' && (
              <button className="btn btn-link" onClick={() => handleUpdate(message, 'CLOSED')}>
                <span className="material-symbols-rounded">check_box_outline_blank</span>
              </button>
            )
          }
          {
            message.status == 'CLOSED' && (
              <button className="btn btn-link" onClick={() => handleUpdate(message, 'ACTIVE')}>
                <span className="material-symbols-rounded">check_box</span>
              </button>
            )
          }
          {
            message.status == 'SPAM' ? (
              <button className="btn btn-link" onClick={() => handleUpdate(message, 'ACTIVE')}>
                <span className="material-symbols-rounded">report_off</span>
              </button>
            ) : (
              <button className="btn btn-link" onClick={() => handleUpdate(message, 'SPAM')}>
                <span className="material-symbols-rounded">report</span>
              </button>
            )
          }
        </span>
      )
    }
  ]

  const headerChildren = (
    <div className="d-md-flex flex-wrap gap-3">
      {
        Object.entries(messageStatus).map(([status, statusLabel], statusIndex) => (
          <Checkbox
            key={statusIndex}
            label={statusLabel}
            checked={params.status == status}
            onChange={() => handleFilter(status)}
          />
        ))
      }
    </div>
  )

  return (
    <div className="messages">
      <List
        columns={columns}
        rows={rows}
        ordering={params.ordering}
        count={count}
        onSearch={handleSearch}
        onNext={hasNextPage ? handleNext : null}
        onReset={handleReset}
        headerChildren={headerChildren}
      />
      <Modal modal={modal} message={modalMessage} />
    </div>
  )
}

export default App
