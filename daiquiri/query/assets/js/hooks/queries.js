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
        queryClient.invalidateQueries({ queryKey: ['jobsTables'] })
        queryClient.invalidateQueries({ queryKey: ['job'] })
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
    queryFn: () => QueryApi.fetchForm(formKey).catch(errors => errors),
    placeholderData: keepPreviousData
  })
}

export const useDropdownsQuery = () => {
  return useQuery({
    queryKey: ['dropdowns'],
    queryFn: () => QueryApi.fetchDropdowns(),
    placeholderData: keepPreviousData
  })
}

export const useDownloadFormsQuery = (jobId) => {
  return useQuery({
    queryKey: ['downloadforms', jobId],
    queryFn: () => QueryApi.fetchDownloadForms(jobId),
    placeholderData: keepPreviousData
  })
}

export const useSubmittedDownloadsQuery = (jobId) => {
  return useQuery({
    queryKey: ['submittedDownloads', jobId],
    queryFn: () => QueryApi.fetchSubmittedDownloads(jobId),
    staleTime: 0,
    refetchInterval: 2500,
  })
}

export const useDownloadFormatsQuery = () => {
  return useQuery({
    queryKey: ['downloadFormats'],
    queryFn: () => QueryApi.fetchDownloadFormats(),
    placeholderData: keepPreviousData
  })
}

export const useJobsQuery = (params) => {
  // this is the query for verbose jobs list
  return useInfiniteQuery({
    queryKey: ['jobs', params],
    queryFn: (context) => QueryApi.fetchJobs({...params, page: context.pageParam})
                                  .catch(error => console.log(error)),
    initialPageParam: '1',
    getNextPageParam: (lastPage) => isNil(lastPage.next) ? null : lastPage.next.match(/page=(\d+)/)[1],
  })
}

export const useJobsIndexQuery = () => {
  // this is the query for jobs list in the sidebar of the submit interface
  return useQuery({
    queryKey: ['jobsIndex'],
    queryFn: () => QueryApi.fetchJobsIndex().catch(error => console.log(error)),
    placeholderData: keepPreviousData
  })
}

export const useJobsTablesQuery = () => {
  // this is the query for tables in the schema and column browser
  return useQuery({
    queryKey: ['jobsTables'],
    queryFn: () => QueryApi.fetchJobsTables(),
    placeholderData: keepPreviousData
  })
}

export const useJobQuery = (jobId) => {
  const queryClient = useQueryClient()

  return useQuery({
    queryKey: ['job', jobId],
    queryFn: () => QueryApi.fetchJob(jobId).then(response => {
      queryClient.invalidateQueries({ queryKey: ['jobsIndex'] })
      return response
    }).catch(errors => errors),
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
        return QueryApi.fetchJobRows(job.id, {column: column, page_size: 1000000})
                             .then((response) => response.results)
      } else {
        return null
      }
    },
    placeholderData: keepPreviousData,
    enabled: job.phase == 'COMPLETED'
  })
}



export const useUserExamplesQuery = () => {
  return useQuery({
    queryKey: ['userExamples'],
    queryFn: () => QueryApi.fetchUserExamples(),
    placeholderData: keepPreviousData
  })
}

/*
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

export const useDownloadFileQuery = (job, downloadKey, downloadId) => {
  return useQuery({
    queryKey: ['downloadJob', job.id, downloadKey, downloadId],
    queryFn: () => QueryApi.fetchDownloadFile(job.id, downloadKey, downloadId),
    enabled: job.phase == 'COMPLETED' && !isEmpty(downloadId),
    refetchOnWindowFocus: false,
    refetchIntervalInBackground: true,
    refetchInterval: false
  })
}
*/

export const useQueuesQuery = () => {
  return useQuery({
    queryKey: ['queues'],
    queryFn: () => QueryApi.fetchQueues(),
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
