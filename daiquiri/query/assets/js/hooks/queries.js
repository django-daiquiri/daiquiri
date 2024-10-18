import { keepPreviousData, useInfiniteQuery, useQuery, useQueryClient } from '@tanstack/react-query'
import { isEmpty, isNil } from 'lodash'

import QueryApi from '../api/QueryApi'
import SimbadApi from '../api/SimbadApi'
import VizierApi from '../api/VizierApi'

const refetchInterval = 4000

export const useStatusQuery = () => {
  const queryClient = useQueryClient()
  const status = queryClient.getQueryData(['status'])

  return useQuery({
    queryKey: ['status'],
    queryFn: () => QueryApi.fetchStatus().then((response) => {
      if (status && (status.hash != response.hash)) {
        queryClient.invalidateQueries({ queryKey: ['jobsIndex'] })
        queryClient.invalidateQueries({ queryKey: ['job'] })
        queryClient.invalidateQueries({ queryKey: ['userSchema'] })
      }
      return response
    }),
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

export const useJobsQuery = (params) => {
  return useInfiniteQuery({
    queryKey: ['jobs', params],
    queryFn: (context) => QueryApi.fetchJobs({...params, page: context.pageParam})
                                  .catch(error => console.log(error)),
    initialPageParam: '1',
    getNextPageParam: (lastPage) => isNil(lastPage.next) ? null : lastPage.next.match(/page=(\d+)/)[1],
  })
}

export const useJobsIndexQuery = () => {
  return useQuery({
    queryKey: ['jobsIndex'],
    queryFn: () => QueryApi.fetchJobsIndex().catch(error => console.log(error)),
    placeholderData: keepPreviousData
  })
}

export const useUserSchemaQuery = () => {
  return useQuery({
    queryKey: ['userSchema'],
    queryFn: () => QueryApi.fetchUserSchema(),
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
    refetchOnWindowFocus: false,
    refetchIntervalInBackground: true,
    refetchInterval: (query) => {
      return (query.state.data && ['QUEUED', 'EXECUTING'].includes(query.state.data.phase)) ? refetchInterval : false
    }
  })
}
