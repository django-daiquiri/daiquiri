import React from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import Users from './components/Users'

const queryClient = new QueryClient()

createRoot(
  document.getElementById('app')
).render(
  <QueryClientProvider client={queryClient}>
    <Users />
  </QueryClientProvider>
)
