import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { isEmpty } from 'lodash'

import CoreApi from '../api/CoreApi'

export const useDataLinksQuery = (dataLinkId) => {
  return useQuery({
    queryKey: ['dataLinks', dataLinkId],
    queryFn: () => CoreApi.fetchDataLinks(dataLinkId),
    placeholderData: keepPreviousData,
    enabled: !isEmpty(dataLinkId)
  })
}

export const useNoteQuery = (url) => {
  return useQuery({
    queryKey: ['note', url],
    queryFn: () => CoreApi.fetchNote(url),
    placeholderData: keepPreviousData,
    enabled: !isEmpty(url)
  })
}
