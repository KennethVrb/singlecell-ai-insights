import { Navigate, useLocation } from "react-router-dom"

import { AuthLoadingScreen } from "@/components/AuthLoadingScreen"
import { AppShellLayout } from "@/components/AppShell"
import { useAuth } from "@/providers/auth-context"

function ProtectedRoute() {
  const { isAuthenticated, isBootstrapping } = useAuth()
  const location = useLocation()

  if (isBootstrapping) {
    return <AuthLoadingScreen />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <AppShellLayout />
}

export default ProtectedRoute
