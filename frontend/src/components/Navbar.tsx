import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from './ui/Button'
import { LogOut, User, Settings, FileText, Shield, FilePlus, CheckCircle, KeyRound, ShoppingBasket, Workflow, Users, Building, Truck } from 'lucide-react'

export function Navbar() {
  const { user, userProfile, signOut, hasRole } = useAuth()
  const navigate = useNavigate()

  const handleSignOut = async () => {
    try {
      await signOut()
      navigate('/login')
    } catch (error) {
      console.error('Sign out failed:', error)
    }
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and Navigation */}
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-indigo-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">A</span>
                </div>
              </div>
              <div className="ml-3">
                <span className="text-xl font-bold text-gray-900">Agentik</span>
                <span className="text-sm text-gray-500 ml-2">B2B Tedarik</span>
              </div>
            </Link>
            
            <div className="ml-10 flex space-x-8">
              <Link
                to="/dashboard"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 border-transparent hover:border-gray-300 transition-colors"
              >
                <FileText className="h-4 w-4 mr-2" />
                Dashboard
              </Link>
              
              {/* Buyer-specific navigation */}
              {hasRole(['buyer', 'admin', 'manager']) && (
                <>
                  <Link
                    to="/rfq/templates"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 border-transparent hover:border-gray-300 transition-colors"
                  >
                    <FilePlus className="h-4 w-4 mr-2" />
                    RFQ Şablonları
                  </Link>
                  <Link
                    to="/rfq/new"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 border-transparent hover:border-gray-300 transition-colors"
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    Yeni RFQ
                  </Link>
                </>
              )}
              
              {/* Supplier-specific navigation */}
              {hasRole(['supplier', 'admin']) && (
                <Link
                  to="/catalog"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 border-transparent hover:border-gray-300 transition-colors"
                >
                  <ShoppingBasket className="h-4 w-4 mr-2" />
                  Katalog
                </Link>
              )}
              
              <Link
                to="/jobs"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 border-transparent hover:border-gray-300 transition-colors"
              >
                <Workflow className="h-4 w-4 mr-2" />
                İşler
              </Link>
              
              <Link
                to="/verification"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 border-transparent hover:border-gray-300 transition-colors"
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Doğrulama
              </Link>
              
              {/* Admin-specific navigation */}
              {hasRole('admin') && (
                <Link
                  to="/admin"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 border-transparent hover:border-gray-300 transition-colors"
                >
                  <Shield className="h-4 w-4 mr-2" />
                  Admin Panel
                </Link>
              )}
              
              {/* Manager-specific navigation */}
              {hasRole(['manager', 'admin']) && (
                <Link
                  to="/team"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 border-transparent hover:border-gray-300 transition-colors"
                >
                  <Users className="h-4 w-4 mr-2" />
                  Takım
                </Link>
              )}
            </div>
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-700">
                  {userProfile?.full_name || 'Kullanıcı'}
                </p>
                <p className="text-xs text-gray-500">
                  {userProfile?.company_name || user?.email}
                  {userProfile?.role && (
                    <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {userProfile.role}
                    </span>
                  )}
                </p>
              </div>
              
              <div className="flex items-center space-x-2">
                <Link to="/settings/2fa" title="2FA Ayarları" className="inline-flex p-2 text-gray-600 hover:text-gray-800">
                  <KeyRound className="h-4 w-4" />
                </Link>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleSignOut}
                  className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50"
                  title="Çıkış Yap"
                >
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
