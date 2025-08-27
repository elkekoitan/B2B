import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { RFQFormPage } from './pages/RFQFormPage'
import { RFQDetailPage } from './pages/RFQDetailPage'
import { RFQTemplatePage } from './pages/RFQTemplatePage'
import { VerificationPage } from './pages/VerificationPage'
import { TwoFactorPage } from './pages/TwoFactorPage'
import { CatalogPage } from './pages/CatalogPage'
import { JobsPage } from './pages/JobsPage'
import { AdminPage } from './pages/AdminPage'
import { LoadingSpinner } from './components/LoadingSpinner'
import { Navbar } from './components/Navbar'
import { ErrorBoundary } from './components/ErrorBoundary'
import { Toaster } from 'sonner'

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return <LoadingSpinner />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return (
    <>
      <Navbar />
      {children}
    </>
  )
}

// Admin Route Component
function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user, userProfile, loading } = useAuth()

  if (loading) {
    return <LoadingSpinner />
  }

  if (!user || !userProfile?.is_admin) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <>
      <Navbar />
      {children}
    </>
  )
}

// Main App Component
function AppRoutes() {
  const { user, loading } = useAuth()

  if (loading) {
    return <LoadingSpinner />
  }

  return (
    <Routes>
      {/* Public Routes */}
      <Route 
        path="/login" 
        element={
          user ? <Navigate to="/dashboard" replace /> : <LoginPage />
        } 
      />
      
      {/* Protected Routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/rfq/new"
        element={
          <ProtectedRoute>
            <RFQFormPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/rfq/templates"
        element={
          <ProtectedRoute>
            <RFQTemplatePage />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/rfq/:id"
        element={
          <ProtectedRoute>
            <RFQDetailPage />
          </ProtectedRoute>
        }
      />
      
      {/* Admin Routes */}
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <AdminPage />
          </AdminRoute>
        }
      />
      <Route
        path="/verification"
        element={
          <ProtectedRoute>
            <VerificationPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings/2fa"
        element={
          <ProtectedRoute>
            <TwoFactorPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/catalog"
        element={
          <ProtectedRoute>
            <CatalogPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/jobs"
        element={
          <ProtectedRoute>
            <JobsPage />
          </ProtectedRoute>
        }
      />
      
      {/* Default Routes */}
      <Route
        path="/"
        element={
          user ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
        }
      />
      
      {/* 404 Route */}
      <Route
        path="*"
        element={
          <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
              <p className="text-gray-600 mb-4">Sayfa bulunamadı</p>
              <button
                onClick={() => window.history.back()}
                className="text-indigo-600 hover:text-indigo-500 font-medium"
              >
                Geri Dön
              </button>
            </div>
          </div>
        }
      />
    </Routes>
  )
}

export default function App() {
  return (
    <ErrorBoundary>
      <Router>
        <AuthProvider>
          <div className="min-h-screen bg-gray-50">
            <AppRoutes />
            <Toaster richColors position="top-right" />
          </div>
        </AuthProvider>
      </Router>
    </ErrorBoundary>
  )
}
