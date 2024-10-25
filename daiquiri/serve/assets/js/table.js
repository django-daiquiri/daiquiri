import React from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import App from './components/App'

const queryClient = new QueryClient()

const appElement = document.getElementById('app')

createRoot(
  document.getElementById('app')
).render(
  <QueryClientProvider client={queryClient}>
    <App schema={appElement.dataset.schema} table={appElement.dataset.table}/>
  </QueryClientProvider>
)
