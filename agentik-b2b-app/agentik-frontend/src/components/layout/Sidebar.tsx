import { 
  LayoutDashboard, 
  FileText, 
  Users, 
  Package, 
  Bell, 
  User, 
  X,
  Plus
} from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'

interface SidebarProps {
  open: boolean
  onClose: () => void
}

const navigation = [
  { name: 'Dashboard', href: '/app/dashboard', icon: LayoutDashboard },
  { name: 'RFQ\'lar', href: '/app/rfqs', icon: FileText },
  { name: 'Tedarikçiler', href: '/app/suppliers', icon: Users },
  { name: 'Tekliflerim', href: '/app/offers', icon: Package },
  { name: 'Bildirimler', href: '/app/notifications', icon: Bell },
]

const quickActions = [
  { name: 'Yeni RFQ Oluştur', href: '/app/rfqs/create', icon: Plus },
]

export default function Sidebar({ open, onClose }: SidebarProps) {
  const location = useLocation()

  return (
    <>
      {/* Mobile backdrop */}
      {open && (
        <div 
          className="fixed inset-0 z-40 lg:hidden bg-black bg-opacity-50"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed top-16 left-0 z-40 w-64 h-full bg-white border-r border-gray-200 transform transition-transform duration-200 ease-in-out lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Mobile close button */}
        <div className="flex justify-end p-4 lg:hidden">
          <button
            onClick={onClose}
            className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="px-4 pb-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href ||
              (item.href !== '/app/dashboard' && location.pathname.startsWith(item.href))
            
            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={onClose}
                className={cn(
                  'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  isActive
                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                    : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
                )}
              >
                <item.icon
                  className={cn(
                    'mr-3 h-5 w-5 flex-shrink-0',
                    isActive ? 'text-blue-700' : 'text-gray-400 group-hover:text-gray-500'
                  )}
                />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* Quick Actions */}
        <div className="px-4 pt-4 border-t border-gray-200">
          <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Hızlı İşlemler
          </h3>
          <nav className="mt-2 space-y-1">
            {quickActions.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                onClick={onClose}
                className="group flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-md hover:text-gray-900 hover:bg-gray-50 transition-colors"
              >
                <item.icon className="mr-3 h-5 w-5 flex-shrink-0 text-gray-400 group-hover:text-gray-500" />
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </>
  )
}