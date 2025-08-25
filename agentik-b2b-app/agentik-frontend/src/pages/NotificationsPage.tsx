import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  Bell, 
  Mail, 
  CheckCircle, 
  AlertTriangle, 
  Info, 
  TrendingUp,
  Trash2,
  MarkAsUnread,
  Filter
} from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'
import { tr } from 'date-fns/locale'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { useAuth } from '@/contexts/AuthContext'
import { useGlobalState } from '@/contexts/GlobalContext'
import { apiClient } from '@/lib/api'
import { cn } from '@/lib/utils'

const notificationIcons = {
  info: Info,
  success: CheckCircle,
  warning: AlertTriangle,
  error: AlertTriangle
}

const notificationColors = {
  info: 'text-blue-500',
  success: 'text-green-500',
  warning: 'text-yellow-500',
  error: 'text-red-500'
}

const typeLabels = {
  info: 'Bilgi',
  success: 'Başarılı',
  warning: 'Uyarı',
  error: 'Hata'
}

export default function NotificationsPage() {
  const { user } = useAuth()
  const { state, markNotificationRead, dispatch } = useGlobalState()
  const [filter, setFilter] = useState<'all' | 'unread' | 'info' | 'success' | 'warning' | 'error'>('all')
  const [selectedIds, setSelectedIds] = useState<string[]>([])

  // Fetch notifications
  const { data: notifications, isLoading } = useQuery({
    queryKey: ['notifications', user?.id],
    queryFn: async () => {
      // Mock data for now - replace with actual API call
      const mockNotifications = [
        {
          id: '1',
          type: 'success' as const,
          title: 'Yeni Teklif Alındı',
          message: 'Büro Mobilyası RFQ\'nıza Mobilya Pro A.Ş. tarafından teklif verildi.',
          read: false,
          createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
          metadata: { rfqId: '1', supplierId: 'supplier-1' }
        },
        {
          id: '2',
          type: 'info' as const,
          title: 'RFQ Yayınlandı',
          message: 'IT Ekipmanları RFQ\'nız başarıyla yayınlandı ve tedarikçilere gönderildi.',
          read: false,
          createdAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 hours ago
          metadata: { rfqId: '2' }
        },
        {
          id: '3',
          type: 'warning' as const,
          title: 'RFQ Süresi Yaklaşıyor',
          message: 'Temizlik Malzemeleri RFQ\'nızın son teslim tarihi 2 gün sonra sona eriyor.',
          read: true,
          createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
          metadata: { rfqId: '3' }
        },
        {
          id: '4',
          type: 'success' as const,
          title: 'İhale Tamamlandı',
          message: 'Kırtasiye Malzemeleri RFQ\'nız için ihale süreci başarıyla tamamlandı.',
          read: true,
          createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
          metadata: { rfqId: '4' }
        },
        {
          id: '5',
          type: 'error' as const,
          title: 'Dosya Yükleme Hatası',
          message: 'RFQ ekinde yüklemeye çalıştığınız dosya formatı desteklenmiyor.',
          read: true,
          createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days ago
          metadata: {}
        }
      ]
      
      await new Promise(resolve => setTimeout(resolve, 500))
      return mockNotifications
    },
    enabled: !!user
  })

  // Filter notifications
  const filteredNotifications = notifications?.filter(notification => {
    if (filter === 'all') return true
    if (filter === 'unread') return !notification.read
    return notification.type === filter
  }) || []

  // Handle mark as read
  const handleMarkAsRead = async (id: string) => {
    try {
      await apiClient.markNotificationRead(id)
      markNotificationRead(id)
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }

  // Handle mark all as read
  const handleMarkAllAsRead = async () => {
    try {
      await apiClient.markAllNotificationsRead()
      // Update all notifications to read
      if (notifications) {
        dispatch({ 
          type: 'SET_NOTIFICATIONS', 
          payload: notifications.map(n => ({ ...n, read: true }))
        })
      }
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error)
    }
  }

  // Handle bulk selection
  const toggleSelection = (id: string) => {
    setSelectedIds(prev => 
      prev.includes(id) 
        ? prev.filter(selectedId => selectedId !== id)
        : [...prev, id]
    )
  }

  const selectAll = () => {
    setSelectedIds(filteredNotifications.map(n => n.id))
  }

  const deselectAll = () => {
    setSelectedIds([])
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const unreadCount = notifications?.filter(n => !n.read).length || 0

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Bell className="h-8 w-8" />
            Bildirimler
            {unreadCount > 0 && (
              <Badge variant="info" className="text-sm">
                {unreadCount} okunmamış
              </Badge>
            )}
          </h1>
          <p className="text-gray-600 mt-1">
            Son güncellemeler ve önemli bildirimler burada.
          </p>
        </div>
        
        {unreadCount > 0 && (
          <Button onClick={handleMarkAllAsRead}>
            <CheckCircle className="h-4 w-4 mr-2" />
            Tümünü Okundu İşaretle
          </Button>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Toplam</p>
                <p className="text-2xl font-bold">{notifications?.length || 0}</p>
              </div>
              <Bell className="h-6 w-6 text-gray-400" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Okunmamış</p>
                <p className="text-2xl font-bold text-blue-600">{unreadCount}</p>
              </div>
              <Mail className="h-6 w-6 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Bu Hafta</p>
                <p className="text-2xl font-bold text-green-600">
                  {notifications?.filter(n => 
                    new Date(n.createdAt) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
                  ).length || 0}
                </p>
              </div>
              <TrendingUp className="h-6 w-6 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Başarılı</p>
                <p className="text-2xl font-bold text-emerald-600">
                  {notifications?.filter(n => n.type === 'success').length || 0}
                </p>
              </div>
              <CheckCircle className="h-6 w-6 text-emerald-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium">Filtrele:</span>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {[
                { key: 'all', label: 'Tümü' },
                { key: 'unread', label: 'Okunmamış' },
                { key: 'info', label: 'Bilgi' },
                { key: 'success', label: 'Başarılı' },
                { key: 'warning', label: 'Uyarı' },
                { key: 'error', label: 'Hata' }
              ].map(({ key, label }) => (
                <Button
                  key={key}
                  variant={filter === key ? "default" : "outline"}
                  size="sm"
                  onClick={() => setFilter(key as any)}
                >
                  {label}
                </Button>
              ))}
            </div>
            
            {selectedIds.length > 0 && (
              <div className="flex items-center gap-2 ml-auto">
                <span className="text-sm text-gray-600">
                  {selectedIds.length} seçili
                </span>
                <Button variant="outline" size="sm" onClick={deselectAll}>
                  Temizle
                </Button>
                <Button variant="destructive" size="sm">
                  <Trash2 className="h-4 w-4 mr-1" />
                  Sil
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Notifications List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Bildirimler ({filteredNotifications.length})</CardTitle>
            {filteredNotifications.length > 0 && (
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={selectAll}>
                  Tümünü Seç
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {filteredNotifications.length === 0 ? (
            <div className="text-center py-12">
              <Bell className="mx-auto h-12 w-12 text-gray-300 mb-4" />
              <p className="text-gray-500 mb-4">
                {filter === 'all' 
                  ? 'Henüz bildirim bulunmamaktadır.' 
                  : `${typeLabels[filter as keyof typeof typeLabels] || 'Filtrelenmiş'} bildirim bulunamadı.`
                }
              </p>
            </div>
          ) : (
            <div className="space-y-1">
              {filteredNotifications.map((notification) => {
                const Icon = notificationIcons[notification.type]
                const colorClass = notificationColors[notification.type]
                const isSelected = selectedIds.includes(notification.id)
                
                return (
                  <div
                    key={notification.id}
                    className={cn(
                      'flex items-start gap-4 p-4 rounded-lg border transition-colors cursor-pointer',
                      notification.read ? 'bg-gray-50' : 'bg-white border-l-4 border-l-blue-500',
                      isSelected && 'bg-blue-50 border-blue-300'
                    )}
                    onClick={() => !notification.read && handleMarkAsRead(notification.id)}
                  >
                    {/* Checkbox */}
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleSelection(notification.id)}
                      onClick={(e) => e.stopPropagation()}
                      className="mt-1"
                    />
                    
                    {/* Icon */}
                    <div className={`p-2 rounded-full ${notification.read ? 'bg-gray-100' : 'bg-blue-100'}`}>
                      <Icon className={cn('h-4 w-4', colorClass)} />
                    </div>
                    
                    {/* Content */}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className={cn(
                          'font-semibold text-sm',
                          notification.read ? 'text-gray-700' : 'text-gray-900'
                        )}>
                          {notification.title}
                        </h3>
                        <Badge variant="outline" className="text-xs">
                          {typeLabels[notification.type]}
                        </Badge>
                        {!notification.read && (
                          <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                        )}
                      </div>
                      <p className={cn(
                        'text-sm mb-2',
                        notification.read ? 'text-gray-600' : 'text-gray-800'
                      )}>
                        {notification.message}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatDistanceToNow(new Date(notification.createdAt), {
                          addSuffix: true,
                          locale: tr
                        })}
                      </p>
                    </div>
                    
                    {/* Actions */}
                    <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                      {!notification.read && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleMarkAsRead(notification.id)}
                          title="Okundu işaretle"
                        >
                          <CheckCircle className="h-4 w-4" />
                        </Button>
                      )}
                      {notification.read && (
                        <Button
                          variant="ghost"
                          size="sm"
                          title="Okunmadı işaretle"
                        >
                          <MarkAsUnread className="h-4 w-4" />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        title="Sil"
                      >
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
