import { Outlet } from 'react-router-dom'
import Header from './Header'
import Sidebar from './Sidebar'
import { useState } from 'react'

export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header 
        onMenuClick={() => setSidebarOpen(!sidebarOpen)}
      />
      
      {/* Content area */}
      <div className="flex">
        {/* Sidebar */}
        <Sidebar 
          open={sidebarOpen} 
          onClose={() => setSidebarOpen(false)} 
        />
        
        {/* Main content */}
        <main className="flex-1 lg:ml-64 pt-16">
          <div className="px-4 sm:px-6 lg:px-8 py-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}