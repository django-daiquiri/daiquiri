import { keepPreviousData, useQuery } from '@tanstack/react-query'
import MetadataApi from '../api/MetadataApi'

export const useUserSchemasQuery = () => {
  return useQuery({
    queryKey: ['schemasUser'],
    queryFn: () => MetadataApi.fetchUserSchemas(),
    placeholderData: keepPreviousData
  })
}
