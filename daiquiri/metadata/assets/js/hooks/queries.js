import { keepPreviousData, useQuery } from '@tanstack/react-query'
import MetadataApi from '../api/MetadataApi'

export const useUserSchemasQuery = () => {
  return useQuery({
    queryKey: ['userSchemas'],
    queryFn: () => MetadataApi.fetchUserSchemas(),
    placeholderData: keepPreviousData
  })
}

export const useUserFunctionsQuery = () => {
  return useQuery({
    queryKey: ['userFunctions'],
    queryFn: () => MetadataApi.fetchUserFunctions(),
    placeholderData: keepPreviousData
  })
}
