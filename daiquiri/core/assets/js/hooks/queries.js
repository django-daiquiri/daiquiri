import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { isEmpty } from 'lodash'

import CoreApi from '../api/CoreApi'

export const useDataLinksQuery = (dataLinkId) => {
  return useQuery({
    queryKey: ['dataLinks', dataLinkId],
    queryFn: () => isEmpty(dataLinkId) ? Promise.resolve(null) : CoreApi.fetchDataLinks(dataLinkId),
    placeholderData: keepPreviousData
  })
}

export const useNoteQuery = (url) => {
  return useQuery({
    queryKey: ['note', url],
    queryFn: () => isEmpty(url) ? Promise.resolve(null) : CoreApi.fetchNote(url),
    placeholderData: keepPreviousData
  })
}
