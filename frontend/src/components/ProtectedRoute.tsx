import { Navigate, useLocation } from "react-router-dom"

import { AuthLoadingScreen } from "@/components/AuthLoadingScreen"
import { MainLayout } from "@/components/MainLayout"
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

  return <MainLayout />
}

export default ProtectedRoute
