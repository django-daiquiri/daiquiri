import { keepPreviousData, useQuery } from '@tanstack/react-query'
import QueryApi from '../api/QueryApi'

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
    queryKey: ['userSchemas'],
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
