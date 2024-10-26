import { useMutation, useQueryClient } from '@tanstack/react-query'

import MetadataApi from '../api/MetadataApi'

export const useUpdateMetadataMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables) => {
      switch (variables.type) {
        case 'schema':
          return MetadataApi.updateSchema(variables.values.id, variables.values)
        case 'table':
          return MetadataApi.updateTable(variables.values.id, variables.values)
        case 'column':
          return MetadataApi.updateColumn(variables.values.id, variables.values)
        case 'function':
          return MetadataApi.updateFunction(variables.values.id, variables.values)
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['managementSchemas'] })
      queryClient.invalidateQueries({ queryKey: ['managementFunctions'] })
    },
    onError: (error) => {
      console.log(error)
    }
  })
}
