import { keepPreviousData, useQuery, useQueryClient } from '@tanstack/react-query'
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

export const useDownloadsQuery = () => {
  return useQuery({
    queryKey: ['downloads'],
    queryFn: () => QueryApi.fetchDownloads(),
    placeholderData: keepPreviousData
  })
}

export const useDownloadFormatsQuery = () => {
  return useQuery({
    queryKey: ['downloadFormats'],
    queryFn: () => QueryApi.fetchDownloadFormats(),
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

export const useJobsQuery = (jobId) => {
  const queryClient = useQueryClient()

  return useQuery({
    queryKey: ['jobs'],
    queryFn: () => QueryApi.fetchJobs({page_size: 1000, archived: ''}).then((response) => {
      const jobs = response.results

      // get the current job from the query cache (from the useJobQuery hook)
      const currentJob = queryClient.getQueryData(['job', jobId])
      jobs.filter(job => job.id == jobId).forEach(job => {
        if (currentJob.phase !== job.phase) {
          queryClient.invalidateQueries({ queryKey: ['job', jobId] })
        }
      })

      return jobs
    }),
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
  const queryClient = useQueryClient()

  return useQuery({
    queryKey: ['job', jobId],
    queryFn: () => QueryApi.fetchJob(jobId).then(response => {
      // reload the jobs list
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      return response
    }),
    placeholderData: keepPreviousData
  })
}

export const useJobColumnsQuery = (job, params) => {
  return useQuery({
    queryKey: ['jobColumns', job.id, params],
    queryFn: () => QueryApi.fetchJobColumns(job.id, params),
    placeholderData: keepPreviousData,
    enabled: job.phase == 'COMPLETED'
  })
}

export const useJobRowsQuery = (job, params) => {
  return useQuery({
    queryKey: ['jobRows', job.id, params],
    queryFn: () => QueryApi.fetchJobRows(job.id, params),
    placeholderData: keepPreviousData,
    enabled: job.phase == 'COMPLETED'
  })
}

export const useJobPlotQuery = (job, column) => {
  return useQuery({
    queryKey: ['jobPlot', job.id, column],
    queryFn: () => {
      if (job.columns.map(column => column.name).includes(column)) {
        return QueryApi.fetchJobRows(job.id, {column: column, page_size: 10000})
                             .then((response) => response.results)
      } else {
        return null
      }
    },
    placeholderData: keepPreviousData,
    enabled: job.phase == 'COMPLETED'
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

export const useDownloadJobQuery = (job, downloadKey, downloadJobId) => {
  return useQuery({
    queryKey: ['downloadJob', job.id, downloadKey, downloadJobId],
    queryFn: () => QueryApi.fetchDownloadJob(job.id, downloadKey, downloadJobId),
    placeholderData: keepPreviousData,
    enabled: job.phase == 'COMPLETED' && !isEmpty(downloadJobId),
    refetchInterval: (query) => {
      return (query.state.data && ['QUEUED', 'EXECUTING'].includes(query.state.data.phase)) ? refetchInterval : false
    }
  })
}
