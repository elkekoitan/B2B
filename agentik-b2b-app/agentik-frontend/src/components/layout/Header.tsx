import { Bell, Menu, Search, User } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useState } from 'react'
import { Link } from 'react-router-dom'

interface HeaderProps {
  onMenuClick: () => void
}

export default function Header({ onMenuClick }: HeaderProps) {
  const { user, signOut } = useAuth()
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('Sign out error:', error)
    }
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-50">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Left side */}
          <div className="flex items-center">
            {/* Mobile menu button */}
            <button
              onClick={onMenuClick}
              className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            >
              <Menu className="h-6 w-6" />
            </button>
            
            {/* Logo */}
            <div className="flex items-center ml-4 lg:ml-0">
              <div className="flex-shrink-0">
                <Link to="/app/dashboard" className="text-2xl font-bold text-blue-600">
                  Agentik B2B
                </Link>
              </div>
            </div>
          </div>

          {/* Search bar */}
          <div className="hidden md:flex items-center flex-1 max-w-md mx-8">
            <div className="relative w-full">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-sm"
                placeholder="RFQ'larda ara..."
              />
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <Link
              to="/app/notifications"
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md relative"
            >
              <Bell className="h-6 w-6" />
              {/* Notification badge */}
              <span className="absolute top-1 right-1 block h-2 w-2 rounded-full bg-red-400"></span>
            </Link>

            {/* User menu */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
              >
                <User className="h-6 w-6" />
                <span className="ml-2 hidden sm:block text-sm font-medium">
                  {user?.email}
                </span>
              </button>

              {/* Dropdown menu */}
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                  <Link
                    to="/app/profile"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    Profilim
                  </Link>
                  <Link
                    to="/app/suppliers/profile"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    Supplier Profili
                  </Link>
                  <button
                    onClick={handleSignOut}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Çıkış Yap
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}