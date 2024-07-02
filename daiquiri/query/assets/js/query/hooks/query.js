import { keepPreviousData, useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
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

export const useUpdateJobMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables) => {
      return QueryApi.updateJob(variables.job.id, variables.values)
    },
    onSuccess: (data, variables) => {
      queryClient.setQueryData(['job', variables.job.id], {...variables.job, ...data})
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      variables.onSuccess()
    },
    onError: (error, variables) => {
      variables.setErrors(error.errors)
    }
  })
}

export const useArchiveJobMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables) => {
      return QueryApi.archiveJob(variables.job.id)
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      variables.onSuccess()
    }
  })
}

export const useAbortJobMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables) => {
      return QueryApi.abortJob(variables.job.id)
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      variables.onSuccess()
    }
  })
}
