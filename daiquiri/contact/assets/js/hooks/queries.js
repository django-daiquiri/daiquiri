import { useInfiniteQuery } from '@tanstack/react-query'
import { isNil } from 'lodash'

import ContactApi from '../api/ContactApi'

export const useMessagesQuery = (params) => {
  return useInfiniteQuery({
    queryKey: ['messages', params],
    queryFn: (context) => ContactApi.fetchMessages({...params, page: context.pageParam}).catch(error => console.log(error)),
    initialPageParam: '1',
    getNextPageParam: (lastPage) => isNil(lastPage.next) ? null : lastPage.next.match(/page=(\d+)/)[1],
  })
}
