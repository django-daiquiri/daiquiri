import { useQuery } from '@tanstack/react-query'

import QueryApi from '../api/QueryApi'

const refetchInterval = 4000

export const useStatusQuery = () => {
  return useQuery({
    queryKey: ['status'],
    queryFn: () => QueryApi.fetchStatus().then((response) => response[0]),
    refetchInterval: refetchInterval
  })
}

export const useFormsQuery = () => {
  return useQuery({
    queryKey: ['forms'],
    queryFn: () => QueryApi.fetchForms(),
    refetchInterval: refetchInterval
  })
}

export const useJobsQuery = () => {
  return useQuery({
    queryKey: ['jobs'],
    queryFn: () => QueryApi.fetchJobs({page_size: 1000, archived: ''}).then((response) => response.results),
    refetchInterval: refetchInterval
  })
}

export const useUserSchema = () => {
  return useQuery({
    queryKey: ['userSchema'],
    queryFn: () => QueryApi.fetchUserSchema(),
    refetchInterval: refetchInterval
  })
}

export const useJobQuery = (jobId) => {
  return useQuery({
    queryKey: ['job', jobId],
    queryFn: () => QueryApi.fetchJob(jobId)
  })
}
