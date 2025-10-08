import { type ReactNode, useState } from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

type QueryProviderProps = {
  children: ReactNode
}

function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30 * 1000,
        refetchOnWindowFocus: false,
      },
    },
  })
}

function QueryProvider({ children }: QueryProviderProps) {
  const [client] = useState(() => createQueryClient())

  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

export { QueryProvider }
