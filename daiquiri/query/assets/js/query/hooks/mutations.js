import { useMutation, useQueryClient } from '@tanstack/react-query'
import QueryApi from '../api/QueryApi'

export const useSubmitJobMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables) => {
      return QueryApi.submitJob(variables.values)
    },
    onSuccess: (data, variables) => {
      variables.loadJob(data.id)
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
    onError: (error, variables) => {
      variables.setErrors(error.errors)
    }
  })
}

export const useUploadJobMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables) => {
      return QueryApi.uploadJob(variables.values)
    },
    onSuccess: (data, variables) => {
      variables.loadJob(data.id)
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
    onError: (error, variables) => {
      variables.setErrors(error.errors)
    }
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