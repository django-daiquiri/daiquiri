import { keepPreviousData, useInfiniteQuery, useQuery } from '@tanstack/react-query'
import { isNil } from 'lodash'

import AuthApi from '../api/AuthApi'

export const useProfilesQuery = (params) => {
  return useInfiniteQuery({
    queryKey: ['profiles', params],
    queryFn: (context) => AuthApi.fetchProfiles({...params, page: context.pageParam}).catch(error => console.log(error)),
    initialPageParam: '1',
    getNextPageParam: (lastPage) => isNil(lastPage.next) ? null : lastPage.next.match(/page=(\d+)/)[1],
  })
}

export const useSettingsQuery = () => {
  return useQuery({
    queryKey: ['settings'],
    queryFn: () => AuthApi.fetchSettings(),
    placeholderData: keepPreviousData
  })
}

export const useGroupsQuery = () => {
  return useQuery({
    queryKey: ['groups'],
    queryFn: () => AuthApi.fetchGroups(),
    placeholderData: keepPreviousData
  })
}
