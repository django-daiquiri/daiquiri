import { keepPreviousData, useQuery } from '@tanstack/react-query'

import ServeApi from '../api/ServeApi'

export const useTableColumnsQuery = (params) => {
  return useQuery({
    queryKey: ['tableColumns', params],
    queryFn: () => ServeApi.fetchColumns(params),
    placeholderData: keepPreviousData
  })
}

export const useTableRowsQuery = (params) => {
  return useQuery({
    queryKey: ['tableRows', params],
    queryFn: () => ServeApi.fetchRows(params),
    placeholderData: keepPreviousData
  })
}
