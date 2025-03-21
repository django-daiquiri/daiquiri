import React from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import Messages from './components/Messages'

const queryClient = new QueryClient()

createRoot(
  document.getElementById('app')
).render(
  <QueryClientProvider client={queryClient}>
    <Messages />
  </QueryClientProvider>
)
