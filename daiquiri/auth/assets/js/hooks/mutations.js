import { useMutation, useQueryClient } from '@tanstack/react-query'

import AuthApi from '../api/AuthApi'

export const useUpdateProfileMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (variables) => {
      return AuthApi.updateProfile(variables.values.id, variables.values, variables.action)
    },
    onSuccess: (data, variables) => {
      // update the profile in the profiles query cache
      queryClient.setQueryData(['profiles', variables.params], (oldData) => {
        return {
          ...oldData,
          pages: oldData.pages.map(page => ({
            ...page, results: page.results.map(row => row.id == data.id ? data : row)
          }))
        }
      })
      variables.modal.hide()
    },
    onError: (error) => {
      console.log(error)
    }
  })
}
