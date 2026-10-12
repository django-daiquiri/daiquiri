import { useMutation, useQueryClient } from '@tanstack/react-query'
import QueryApi from '../api/QueryApi'

export const useSubmitJobMutation = () => {
  return useMutation({
    mutationFn: (variables) => {
      return QueryApi.submitJob(variables.values, variables.formKey)
    },
    onSuccess: (data, variables) => {
      variables.loadJob(data.id)
    },
    onError: (error, variables) => {
      variables.setErrors(error.errors)
    }
  })
}

export const useUploadJobMutation = () => {
  return useMutation({
    mutationFn: (variables) => {
      return QueryApi.uploadJob(variables.values)
    },
    onSuccess: (data, variables) => {
      variables.loadJob(data.id)
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
      queryClient.invalidateQueries({ queryKey: ['job', variables.job.id] })
      queryClient.invalidateQueries({ queryKey: ['submittedDownloads', variables.job.id] })
      variables.onSuccess()
    }
  })
}

export const useArchiveAllJobsMutation = () => {
    const queryClient = useQueryClient()
    return useMutation({
      mutationFn: (jobs) => {
        return QueryApi.archiveJob(jobs)
      },
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['jobs'] })
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

export const useSubmitDownloadJobMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables) => {
      return QueryApi.submitDownloadJob(variables.job.id, variables.downloadKey, variables.data)
    },
    onSuccess: async (data, variables) => {
      await queryClient.invalidateQueries({ queryKey: ['submittedDownloads', variables.job.id] })
      variables.onSuccess?.(data)
    },
    onSettled: (data, error, variables) => {
      variables.onSettled?.()
    }
  })
}

export const useAbortDownloadJobMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables) => {
      return QueryApi.abortDownloadJob(
        variables.job.id, variables.downloadKey, variables.downloadJobId
      )
    },
    onSuccess: async (data, variables) => {
      await queryClient.invalidateQueries({ queryKey: ['submittedDownloads', variables.job.id] })
      variables.onSuccess?.(data)
    }
  })
}
