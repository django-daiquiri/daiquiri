import { useMutation, useQueryClient } from '@tanstack/react-query'

import ContactApi from '../api/ContactApi'

export const useUpdateMessageMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables) => {
      return ContactApi.updateMessage(variables.message.id, variables.message)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messages'] })
    },
    onError: (error) => {
      console.log(error)
    }
  })
}
