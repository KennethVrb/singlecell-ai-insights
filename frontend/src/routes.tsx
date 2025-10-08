import { Navigate, createBrowserRouter } from "react-router-dom"

import ProtectedRoute from "@/components/ProtectedRoute"
import LoginPage from "@/pages/LoginPage"
import RunDetailPage from "@/pages/RunDetailPage"
import RunsPage from "@/pages/RunsPage"

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/runs" replace />,
  },
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        path: "/runs",
        element: <RunsPage />,
      },
      {
        path: "/runs/:runId",
        element: <RunDetailPage />,
      },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/runs" replace />,
  },
])
