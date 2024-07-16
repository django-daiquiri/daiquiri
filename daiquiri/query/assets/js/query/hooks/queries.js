import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { isEmpty } from 'lodash'

import QueryApi from '../api/QueryApi'
import SimbadApi from '../api/SimbadApi'
import VizierApi from '../api/VizierApi'

const refetchInterval = 4000

export const useStatusQuery = () => {
  return useQuery({
    queryKey: ['status'],
    queryFn: () => QueryApi.fetchStatus().then((response) => response[0]),
    refetchInterval: refetchInterval,
    placeholderData: keepPreviousData
  })
}

export const useFormsQuery = () => {
  return useQuery({
    queryKey: ['forms'],
    queryFn: () => QueryApi.fetchForms(),
    placeholderData: keepPreviousData
  })
}

export const useFormQuery = (formKey) => {
  return useQuery({
    queryKey: ['form', formKey],
    queryFn: () => QueryApi.fetchForm(formKey),
    placeholderData: keepPreviousData
  })
}

export const useQueryLanguagesQuery = () => {
  return useQuery({
    queryKey: ['queryLanguages'],
    queryFn: () => QueryApi.fetchQueryLanguages(),
    placeholderData: keepPreviousData
  })
}

export const useQueuesQuery = () => {
  return useQuery({
    queryKey: ['queues'],
    queryFn: () => QueryApi.fetchQueues(),
    placeholderData: keepPreviousData
  })
}

export const useDropdownsQuery = () => {
  return useQuery({
    queryKey: ['drowdowns'],
    queryFn: () => QueryApi.fetchDropdowns(),
    placeholderData: keepPreviousData
  })
}

export const useJobsQuery = () => {
  return useQuery({
    queryKey: ['jobs'],
    queryFn: () => QueryApi.fetchJobs({page_size: 1000, archived: ''}).then((response) => response.results),
    refetchInterval: refetchInterval,
    placeholderData: keepPreviousData
  })
}

export const useUserSchemaQuery = () => {
  return useQuery({
    queryKey: ['userSchema'],
    queryFn: () => QueryApi.fetchUserSchema(),
    refetchInterval: refetchInterval,
    placeholderData: keepPreviousData
  })
}

export const useUserExamplesQuery = () => {
  return useQuery({
    queryKey: ['userExamples'],
    queryFn: () => QueryApi.fetchUserExamples(),
    placeholderData: keepPreviousData
  })
}

export const useJobQuery = (jobId) => {
  return useQuery({
    queryKey: ['job', jobId],
    queryFn: () => QueryApi.fetchJob(jobId),
    placeholderData: keepPreviousData
  })
}

export const useJobColumnsQuery = (jobId, params) => {
  return useQuery({
    queryKey: ['jobColumns', jobId, params],
    queryFn: () => QueryApi.fetchJobColumns(jobId, params),
    placeholderData: keepPreviousData
  })
}

export const useJobRowsQuery = (jobId, params) => {
  return useQuery({
    queryKey: ['jobRows', jobId, params],
    queryFn: () => QueryApi.fetchJobRows(jobId, params),
    placeholderData: keepPreviousData
  })
}

export const useSimbadQuery = (url, search) => {
  return useQuery({
    queryKey: ['simbad', search],
    queryFn: () => SimbadApi.search(url, search),
    placeholderData: keepPreviousData,
    enabled: !isEmpty(search)
  })
}

export const useVizierQuery = (url, search) => {
  return useQuery({
    queryKey: ['vizier', search],
    queryFn: () => VizierApi.search(url, search),
    placeholderData: keepPreviousData,
    enabled: !isEmpty(search)
  })
}
