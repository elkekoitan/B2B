import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './contexts/AuthContext'
import { GlobalProvider } from './contexts/GlobalContext'
import ErrorBoundary from './components/ErrorBoundary'
import { Toaster } from 'sonner'

// Import pages
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import RFQListPage from './pages/RFQListPage'
import RFQDetailPage from './pages/RFQDetailPage'
import CreateRFQPage from './pages/CreateRFQPage'
import SupplierListPage from './pages/SupplierListPage'
import SupplierProfilePage from './pages/SupplierProfilePage'
import OffersPage from './pages/OffersPage'
import NotificationsPage from './pages/NotificationsPage'
import ProfilePage from './pages/ProfilePage'
import AuthCallbackPage from './pages/AuthCallbackPage'

// Import components
import ProtectedRoute from './components/ProtectedRoute'
import MainLayout from './components/layout/MainLayout'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <GlobalProvider>
          <AuthProvider>
            <Router>
              <div className="min-h-screen bg-gray-50">
                <Routes>
                  {/* Public routes */}
                  <Route path="/" element={<HomePage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route path="/auth/callback" element={<AuthCallbackPage />} />
                  
                  {/* Protected routes with main layout */}
                  <Route path="/app" element={
                    <ProtectedRoute>
                      <MainLayout />
                    </ProtectedRoute>
                  }>
                    <Route index element={<Navigate to="/app/dashboard" replace />} />
                    <Route path="dashboard" element={<DashboardPage />} />
                    <Route path="rfqs" element={<RFQListPage />} />
                    <Route path="rfqs/create" element={<CreateRFQPage />} />
                    <Route path="rfqs/:id" element={<RFQDetailPage />} />
                    <Route path="suppliers" element={<SupplierListPage />} />
                    <Route path="suppliers/profile" element={<SupplierProfilePage />} />
                    <Route path="offers" element={<OffersPage />} />
                    <Route path="notifications" element={<NotificationsPage />} />
                    <Route path="profile" element={<ProfilePage />} />
                  </Route>
                  
                  {/* Catch all route */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
                
                {/* Global toast notifications */}
                <Toaster richColors position="top-right" />
              </div>
            </Router>
          </AuthProvider>
        </GlobalProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App