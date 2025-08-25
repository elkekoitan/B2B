import React from 'react'
import { Loader2 } from 'lucide-react'

export function LoadingSpinner() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-indigo-600" />
        <p className="text-gray-600 text-lg">Yükleniyor...</p>
        <p className="text-gray-500 text-sm mt-2">Lütfen bekleyin</p>
      </div>
    </div>
  )
}