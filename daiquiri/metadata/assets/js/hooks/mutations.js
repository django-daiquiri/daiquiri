import { useMutation, useQueryClient } from '@tanstack/react-query'

import MetadataApi from '../api/MetadataApi'

export const useCreateMetadataMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables) => {
      switch (variables.values.type) {
        case 'schema':
          return MetadataApi.createSchema(variables.values)
        case 'table':
          return MetadataApi.createTable(variables.values)
        case 'view':
          return MetadataApi.createTable(variables.values)
        case 'column':
          return MetadataApi.createColumn(variables.values)
        case 'function':
          return MetadataApi.createFunction(variables.values)
      }
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['managementSchemas'] })
      queryClient.invalidateQueries({ queryKey: ['managementFunctions'] })
      variables.setActiveItem({ type: variables.values.type, ...data })
      variables.modal.hide()
    },
    onError: (error) => {
      console.log(error)
    }
  })
}

export const useUpdateMetadataMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables) => {
      switch (variables.values.type) {
        case 'schema':
          return MetadataApi.updateSchema(variables.values.id, variables.values)
        case 'table':
          return MetadataApi.updateTable(variables.values.id, variables.values)
        case 'view':
          return MetadataApi.updateTable(variables.values.id, variables.values)
        case 'column':
          return MetadataApi.updateColumn(variables.values.id, variables.values)
        case 'function':
          return MetadataApi.updateFunction(variables.values.id, variables.values)
      }
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['managementSchemas'] })
      queryClient.invalidateQueries({ queryKey: ['managementFunctions'] })
      variables.setSuccess(true)

      // set the success flag and start the timeout to remove it. the flag is actually
      // the stored timeout, so we can cancel any old timeout before starting the a new one
      clearTimeout(variables.success)
      variables.setSuccess(setTimeout(() => variables.setSuccess(null), 1000))
    },
    onError: (error) => {
      console.log(error)
    }
  })
}

export const useDiscoverMetadataMutation = () => {
  return useMutation({
    mutationFn: (variables) => {
      switch (variables.values.type) {
        case 'table':
          return MetadataApi.discoverTable(variables.values.id)
        case 'view':
          return MetadataApi.discoverTable(variables.values.id)
        case 'column':
          return MetadataApi.discoverColumn(variables.values.id)
      }
    },
    onSuccess: (data, variables) => {
      variables.setValues({ type: variables.values.type, ...data })
    },
    onError: (error) => {
      console.log(error)
    }
  })
}
