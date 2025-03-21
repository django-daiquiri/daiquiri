import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { isNil, isNumber } from 'lodash'

import MetadataApi from '../api/MetadataApi'

export const useManagementSchemasQuery = () => {
  return useQuery({
    queryKey: ['managementSchemas'],
    queryFn: () => MetadataApi.fetchManagementSchemas(),
    placeholderData: keepPreviousData,
  })
}

export const useManagementFunctionsQuery = () => {
  return useQuery({
    queryKey: ['managementFunctions'],
    queryFn: () => MetadataApi.fetchManagementFunctions(),
    placeholderData: keepPreviousData
  })
}

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

export const useMetadataQuery = ({ type, id }) => {
  return useQuery({
    queryKey: ['metadata', type, id],
    queryFn: () => {
      switch (type) {
        case 'schema':
          return MetadataApi.fetchSchema(id).then(response => ({ type, ...response }))
        case 'table':
          return MetadataApi.fetchTable(id).then(response => ({ type, ...response }))
        case 'view':
          return MetadataApi.fetchTable(id).then(response => ({ type, ...response }))
        case 'column':
          return MetadataApi.fetchColumn(id).then(response => ({ type, ...response }))
        case 'function':
          return MetadataApi.fetchFunction(id).then(response => ({ type, ...response }))
      }
    },
    placeholderData: keepPreviousData,
    enabled: !isNil(type) && isNumber(id)
  })
}

export const useLicensesQuery = () => {
  return useQuery({
    queryKey: ['licenses'],
    queryFn: () => MetadataApi.fetchLicenses(),
    placeholderData: keepPreviousData
  })
}

export const useAccessLevelsQuery = () => {
  return useQuery({
    queryKey: ['accessLevels'],
    queryFn: () => MetadataApi.fetchAccessLevels(),
    placeholderData: keepPreviousData
  })
}

export const useMetaQuery = () => {
  return useQuery({
    queryKey: ['meta'],
    queryFn: () => MetadataApi.fetchMeta(),
    placeholderData: keepPreviousData
  })
}
