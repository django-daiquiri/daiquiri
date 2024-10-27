import React, { useState } from 'react'
import { isNil, omit } from 'lodash'

import { useModal } from 'daiquiri/core/assets/js/hooks/modal'

import { useMessagesQuery } from '../hooks/queries'
import { useUpdateMessageMutation } from '../hooks/mutations'
import { messageStatus, messageStatusBadge } from '../constants/messages'

import Checkbox from 'daiquiri/core/assets/js/components/form/Checkbox'
import List from 'daiquiri/core/assets/js/components/list/List'

import ShowModal from './ShowModal.js'

const Messages = () => {
  const initialParams = {}

  const [params, setParams] = useState(initialParams)

  const modal = useModal()
  const [values, setValues] = useState({})

  const mutation = useUpdateMessageMutation()

  const { data, fetchNextPage, hasNextPage } = useMessagesQuery(params)

  const count = isNil(data) ? null : interpolate(ngettext(
    'One contact message found.', '%s contact messages found', data.pages[0].count
  ), [data.pages[0].count])

  const rows = isNil(data) ? [] : data.pages.reduce((messages, page) => {
    return [...messages, ...page.results]
  }, [])

  const handleModal = (message) => {
    setValues(message)
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
    setParams(initialParams)
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
          <a href={message.mailto}>
            <i className="bi bi-reply"></i>
          </a>
          <button className="btn btn-link" onClick={() => handleModal(message)}>
            <i className="bi bi-eye"></i>
          </button>
          {
            message.status == 'ACTIVE' && <>
              <button className="btn btn-link" title={gettext('Mark as closed')}
                      onClick={() => handleUpdate(message, 'CLOSED')}>
                <i className="bi bi-check-circle"></i>
              </button>
              <button className="btn btn-link" title={gettext('Mark as spam')}
                      onClick={() => handleUpdate(message, 'SPAM')}>
                <i className="bi bi-exclamation-octagon"></i>
              </button>
            </>
          }
          {
            (message.status == 'CLOSED' || message.status == 'SPAM') && (
              <button className="btn btn-link" title={gettext('Mark as active')}
                      onClick={() => handleUpdate(message, 'ACTIVE')}>
                <i className="bi bi-circle"></i>
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
      <ShowModal modal={modal} message={values} />
    </div>
  )
}

export default Messages
