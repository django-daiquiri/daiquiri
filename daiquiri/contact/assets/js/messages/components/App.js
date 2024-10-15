import React, { useState } from 'react'
import { isNil } from 'lodash'

import { useModal } from 'daiquiri/core/assets/js/hooks/modal'

import List from 'daiquiri/core/assets/js/components/list/List'

import { useMessagesQuery } from '../hooks/queries'
import { useUpdateMessageMutation } from '../hooks/mutations'
import { messageStatusBadge } from '../constants/messages'

import Modal from './Modal.js'

const App = () => {
  const initalParams = {
    spam: false
  }

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

  const handleOrdering = (column) => {
    const ordering = (params.ordering == column.name) ? '-' + column.name : column.name
    setParams({ ...params, ordering })
  }

  const handleShowModal = (message) => {
    setModalMessage(message)
    modal.show()
  }

  const handleUpdateMessage = (message, status) => {
    mutation.mutate({ message: {...message, status }})
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

  const columns = [
    {
      name: 'id', label: gettext('ID'), width: '5%'
    },
    {
      name: 'subject', label: gettext('Subject'), width: '15%', onOrder: handleOrdering, formatter: (message) => (
        <button className="btn btn-link" onClick={() => handleShowModal(message)}>{message.subject}</button>
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
          <button className="btn btn-link" onClick={() => handleShowModal(message)}>
            <span className="material-symbols-rounded">visibility</span>
          </button>
          {
            message.status == 'ACTIVE' && (
              <button className="btn btn-link" onClick={() => handleUpdateMessage(message, 'CLOSED')}>
                <span className="material-symbols-rounded">check_box_outline_blank</span>
              </button>
            )
          }
          {
            message.status == 'CLOSED' && (
              <button className="btn btn-link" onClick={() => handleUpdateMessage(message, 'ACTIVE')}>
                <span className="material-symbols-rounded">check_box</span>
              </button>
            )
          }
          {
            message.status == 'SPAM' ? (
              <button className="btn btn-link" onClick={() => handleUpdateMessage(message, 'ACTIVE')}>
                <span className="material-symbols-rounded">report_off</span>
              </button>
            ) : (
              <button className="btn btn-link" onClick={() => handleUpdateMessage(message, 'SPAM')}>
                <span className="material-symbols-rounded">report</span>
              </button>
            )
          }
        </span>
      )
    }
  ]

  const buttons = [
    {
      label: params.spam ? gettext('Show non-spam') : gettext('Show spam'),
      onClick: () => setParams({page: 1, spam: !params.spam})
    }
  ]

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
        buttons={buttons}
        checkboxes={{}}
      />
      <Modal modal={modal} message={modalMessage} />
    </div>
  )
}

export default App
