import React, { useState } from 'react'
import { isEmpty, isNil } from 'lodash'

import { useModal } from 'daiquiri/core/assets/js/hooks/modal'
import { isStaff, userId } from 'daiquiri/core/assets/js/utils/meta'

import List from 'daiquiri/core/assets/js/components/list/List'

import { useGroupsQuery, useProfilesQuery, useSettingsQuery } from '../hooks/queries'
import { useUpdateProfileMutation } from '../hooks/mutations'

import ShowModal from './ShowModal.js'
import UpdateModal from './UpdateModal.js'
import ConfirmModal from './ConfirmModal.js'

const App = () => {
  const initalParams = {
    ordering: '-user__date_joined'
  }

  const [params, setParams] = useState(initalParams)

  const showModal = useModal()
  const updateModal = useModal()
  const activateModal = useModal()
  const enableModal = useModal()
  const disableModal = useModal()
  const confirmModal = useModal()
  const rejectModal = useModal()

  const [values, setValues] = useState({})
  const [errors, setErrors] = useState({})

  const mutation = useUpdateProfileMutation()

  const { data: settings } = useSettingsQuery()
  const { data: groups } = useGroupsQuery()

  const { data, fetchNextPage, hasNextPage } = useProfilesQuery(params)

  const count = isNil(data) ? null : interpolate(ngettext(
    'One user found.', '%s users found', data.pages[0].count
  ), [data.pages[0].count])

  const rows = isNil(data) ? [] : data.pages.reduce((profiles, page) => {
    return [...profiles, ...page.results]
  }, [])

  const handleOrdering = (column) => {
    const ordering = (params.ordering == column.name) ? '-' + column.name : column.name
    setParams({ ...params, ordering })
  }

  const handleModal = (modal, profile) => {
    setValues(profile)
    modal.show()
  }

  const handleSearch = (search) => {
    setParams({ ...params, search })
  }

  const handleReset = () => {
    setParams(initalParams)
  }

  const handleUpdate = (modal, action) => {
    mutation.mutate({ values, action, modal, params, setErrors })
  }

  const columns = [
    {
      name: 'user__username', label: gettext('Name (Username)'), onOrder: handleOrdering, width: '20%',
      formatter: (profile) => (
        <div className="d-flex gap-1">
          <button className="btn btn-link" title={gettext('Show user details')}
                  onClick={() => handleModal(showModal, profile)}>{profile.full_name}</button>
          <i className="d-block">({profile.user.username})</i>
        </div>
      )
    },
    {
      name: 'user__email', label: gettext('Email'), onOrder: handleOrdering,  width: '20%',
      formatter: (profile) => (
        <a href={`mailto:${profile.user.email}`}>{profile.user.email}</a>
      )
    },
    {
      name: 'user__date_joined', label: gettext('Date joined'), onOrder: handleOrdering,  width: '20%',
      formatter: (profile) => profile.user.date_joined_label
    },
    {
      name: 'status', label: gettext('Status'), width: '15%', formatter: (profile) => <>
        {
          profile.user.is_superuser && (
            <span className="badge text-bg-success me-1">{gettext('superuser')}</span>
          )
        }
        {
          profile.user.is_staff && !profile.user.is_superuser && (
            <span className="badge text-bg-success me-1">{gettext('staff')}</span>
          )
        }
        {
          profile.user.is_active && !profile.is_pending && !profile.is_confirmed && (
            <span className="badge text-bg-secondary me-1">{gettext('active')}</span>
          )
        }
        {
          !profile.user.is_active && (
            <span className="badge text-bg-danger me-1">{gettext('disabled')}</span>
          )
        }
        {
          profile.is_pending && (
            <span className="badge text-bg-primary me-1">{gettext('pending')}</span>
          )
        }
        {
          profile.is_confirmed && (
            <span className="badge text-bg-primary me-1">{gettext('confirmed')}</span>
          )
        }
      </>
    },
    {
      name: 'groups', label: gettext('Groups'), width: '15%', formatter: (profile) => <>
        {
          profile.user.groups.map((group, groupIndex) => (
            <span key={groupIndex} className="badge text-bg-secondary me-1">{groups.find(g => g.id == group).name}</span>
          ))
        }
      </>
    },
    {
      width: '10%', formatter: (profile) => (
        <span className="d-flex gap-1 flex-wrap justify-content-end">
          <button className="btn btn-link" title={gettext('Show user details')}
                  onClick={() => handleModal(showModal, profile)}>
            <span className="material-symbols-rounded">visibility</span>
          </button>

          <button className="btn btn-link" title={gettext('Update user')}
                  onClick={() => handleModal(updateModal, profile)}>
            <span className="material-symbols-rounded">edit</span>
          </button>

          {
            profile.id != userId && !profile.is_pending && <>
              {
                !profile.user.is_active && (
                  <button className="btn btn-link" title={gettext('Enable user')}
                          onClick={() => handleModal(enableModal, profile)}>
                    <span className="material-symbols-rounded">check_circle</span>
                  </button>
                )
              }
              {
                profile.user.is_active && (
                    <button className="btn btn-link" title={gettext('Disable user')}
                            onClick={() => handleModal(disableModal, profile)}>
                      <span className="material-symbols-rounded">cancel</span>
                    </button>
                  )
              }
            </>
          }

          {
            settings.AUTH_WORKFLOW == 'confirmation' && profile.is_pending && !profile.is_confirmed && <>
              <button className="btn btn-link" title={gettext('Confirm user')}
                      onClick={() => handleModal(confirmModal, profile)}>
                <span className="material-symbols-rounded">thumb_up</span>
              </button>

              <button className="btn btn-link" title={gettext('Reject user')}
                      onClick={() => handleModal(rejectModal, profile)}>
                <span className="material-symbols-rounded">thumb_down</span>
              </button>
            </>
          }

          {
            settings.AUTH_WORKFLOW == 'activation' && profile.is_pending && <>
              <button className="btn btn-link" title={gettext('Activate user')}
                      onClick={() => handleModal(activateModal, profile)}>
                <span className="material-symbols-rounded">check_circle</span>
              </button>

              <button className="btn btn-link" title={gettext('Reject user')}
                      onClick={() => handleModal(rejectModal, profile)}>
                <span className="material-symbols-rounded">cancel</span>
              </button>
            </>
          }

          {
            isStaff && <>
              {
                settings.AUTH_WORKFLOW == 'confirmation' && profile.is_pending && profile.is_confirmed && (
                  <button className="btn btn-link" title={gettext('Activate user')}
                          onClick={() => handleModal(activateModal, profile)}>
                    <span className="material-symbols-rounded">check_circle</span>
                  </button>
                )
              }

              <a href={profile.user_admin_url} title={gettext('User Admin')} target="_blank" rel="noreferrer">
                <span className="material-symbols-rounded">person</span>
              </a>

              <a href={profile.profile_admin_url} title={gettext('Profile Admin')} target="_blank" rel="noreferrer">
                <span className="material-symbols-rounded">account_circle</span>
              </a>
            </>
          }
        </span>
      )
    }
  ]

  return !isEmpty(settings) && !isEmpty(groups) && (
    <div className="messages">
      <List
        columns={columns}
        rows={rows}
        ordering={params.ordering}
        count={count}
        onSearch={handleSearch}
        onNext={hasNextPage ? fetchNextPage : null}
        onReset={handleReset}
        checkboxes={{}}
      />
      <ShowModal
        modal={showModal}
        values={values}
        details={settings.AUTH_DETAIL_KEYS}
      />
      <UpdateModal
        modal={updateModal}
        values={values}
        errors={errors}
        details={settings.AUTH_DETAIL_KEYS}
        groups={groups}
        setValues={setValues}
        onSubmit={handleUpdate}
      />
      <ConfirmModal modal={activateModal} label={gettext('Activate user')} action="activate" onSubmit={handleUpdate}/>
      <ConfirmModal modal={disableModal} label={gettext('Disable user')} action="disable" onSubmit={handleUpdate}/>
      <ConfirmModal modal={confirmModal} label={gettext('Confirm user')} action="confirm" onSubmit={handleUpdate}/>
      <ConfirmModal modal={enableModal} label={gettext('Enable user')} action="enable" onSubmit={handleUpdate}/>
      <ConfirmModal modal={rejectModal} label={gettext('Reject user')} action="reject" onSubmit={handleUpdate}/>
    </div>
  )
}

export default App
