import React from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import Table from './components/Table'

const queryClient = new QueryClient()

const appElement = document.getElementById('app')

createRoot(appElement).render(
  <QueryClientProvider client={queryClient}>
    <Table schema={appElement.dataset.schema} table={appElement.dataset.table} search={appElement.dataset.search}/>
  </QueryClientProvider>
)
