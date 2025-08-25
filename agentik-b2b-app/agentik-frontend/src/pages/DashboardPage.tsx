import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/contexts/AuthContext'
import { apiClient } from '@/lib/api'
import { supabase } from '@/lib/supabase'
import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import StatsCards from '@/components/Dashboard/StatsCards'
import DashboardRFQList from '@/components/Dashboard/DashboardRFQList'
import ActivityFeed from '@/components/Dashboard/ActivityFeed'
import { 
  Plus, 
  TrendingUp, 
  AlertCircle, 
  CheckCircle, 
  Bell,
  Eye,
  Calendar
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

export default function DashboardPage() {
  const { user, session } = useAuth()
  const [realtimeData, setRealtimeData] = useState<any>(null)

  // Set API token when session changes
  useEffect(() => {
    if (session?.access_token) {
      apiClient.setToken(session.access_token)
    }
  }, [session])

  // Dashboard stats query - Enhanced
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats', user?.id],
    queryFn: async () => {
      // Enhanced mock data with more realistic values
      return {
        totalRFQs: 23,
        pendingRFQs: 7,
        completedRFQs: 16,
        totalOffers: 89,
        avgResponseTime: '1.8 gün',
        activeSuppliers: 34,
        totalBudget: 2150000,
        savedAmount: 285000
      }
    },
    enabled: !!user
  })

  // RFQs query - Extended mock data
  const { data: rfqs, isLoading: rfqsLoading } = useQuery({
    queryKey: ['dashboard-rfqs', user?.id],
    queryFn: async () => {
      // Extended mock data for better demonstration
      return [
        {
          id: '1',
          title: 'Büro Mobilyası Tedariki',
          company: 'ABC Şirketi',
          status: 'published' as const,
          deadline: '2025-01-15T00:00:00Z',
          offerCount: 5,
          createdAt: '2025-01-01T10:00:00Z',
          budget: 150000,
          category: 'Mobilya'
        },
        {
          id: '2',
          title: 'IT Ekipmanları ve Yazılım Lisansları',
          company: 'TechCorp A.Ş.',
          status: 'draft' as const,
          deadline: '2025-01-20T00:00:00Z',
          offerCount: 0,
          createdAt: '2025-01-02T14:30:00Z',
          budget: 500000,
          category: 'Teknoloji'
        },
        {
          id: '3',
          title: 'Temizlik ve Hijyen Malzemeleri',
          company: 'CleanPro Ltd.',
          status: 'published' as const,
          deadline: '2025-01-25T00:00:00Z',
          offerCount: 8,
          createdAt: '2025-01-03T09:15:00Z',
          budget: 75000,
          category: 'Temizlik'
        },
        {
          id: '4',
          title: 'Kargo ve Lojistik Hizmetleri',
          company: 'LogiCorp A.Ş.',
          status: 'closed' as const,
          deadline: '2025-01-10T00:00:00Z',
          offerCount: 12,
          createdAt: '2024-12-20T16:45:00Z',
          budget: 300000,
          category: 'Lojistik'
        },
        {
          id: '5',
          title: 'Güvenlik Hizmetleri',
          company: 'SecureMax Ltd.',
          status: 'awarded' as const,
          deadline: '2024-12-30T00:00:00Z',
          offerCount: 6,
          createdAt: '2024-12-15T11:20:00Z',
          budget: 200000,
          category: 'Güvenlik'
        }
      ]
    },
    enabled: !!user
  })

  // Urgent actions query
  const { data: urgentActions, isLoading: urgentLoading } = useQuery({
    queryKey: ['urgent-actions', user?.id],
    queryFn: async () => {
      // Mock urgent actions
      return [
        {
          id: '1',
          type: 'deadline_approaching',
          title: 'RFQ son tarihi yaklaşıyor',
          message: 'Büro Mobilyası RFQ\'ının son tarihi 5 gün sonra',
          rfqId: '1',
          priority: 'high' as const,
          dueDate: '2025-01-15T00:00:00Z'
        },
        {
          id: '2',
          type: 'new_offers',
          title: 'Yeni teklifler var',
          message: '3 yeni teklif değerlendirme bekliyor',
          rfqId: '3',
          priority: 'medium' as const,
          count: 3
        }
      ]
    },
    enabled: !!user
  })

  // Activities query
  const { data: activities, isLoading: activitiesLoading } = useQuery({
    queryKey: ['dashboard-activities', user?.id],
    queryFn: async () => {
      // Mock data for now - replace with actual API call
      return [
        {
          id: '1',
          type: 'offer_received' as const,
          title: 'Yeni Teklif Alındı',
          description: 'Büro Mobilyası RFQ\'ına yeni bir teklif geldi',
          timestamp: '2025-01-10T14:30:00Z'
        },
        {
          id: '2',
          type: 'rfq_created' as const,
          title: 'RFQ Oluşturuldu',
          description: 'IT Ekipmanları RFQ\'ı oluşturuldu',
          timestamp: '2025-01-10T10:15:00Z'
        }
      ]
    },
    enabled: !!user
  })

  // Real-time subscription setup
  useEffect(() => {
    if (!user) return

    const channel = supabase
      .channel('dashboard-updates')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'rfqs',
          filter: `user_id=eq.${user.id}`
        },
        (payload) => {
          console.log('RFQ update:', payload)
          // Invalidate relevant queries to refetch data
          // queryClient.invalidateQueries(['dashboard-stats'])
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [user])

  const isLoading = statsLoading || rfqsLoading || activitiesLoading || urgentLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="border-b pb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Hoş geldiniz, {user?.user_metadata?.full_name || user?.email}. RFQ süreçlerinizi burada takip edebilirsiniz.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" asChild>
              <Link to="/app/rfqs" className="gap-2">
                <Eye className="h-4 w-4" />
                Tüm RFQ'lar
              </Link>
            </Button>
            <Button asChild>
              <Link to="/app/rfqs/create" className="gap-2">
                <Plus className="h-4 w-4" />
                Yeni RFQ Oluştur
              </Link>
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && <StatsCards stats={stats} />}

      {/* Urgent Actions */}
      {urgentActions && urgentActions.length > 0 && (
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-700">
              <AlertCircle className="h-5 w-5" />
              Acil İşlemler
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {urgentActions.map((action) => (
                <div key={action.id} className="flex items-center justify-between p-3 bg-white rounded-lg border">
                  <div className="flex items-center gap-3">
                    {action.type === 'deadline_approaching' ? (
                      <Calendar className="h-5 w-5 text-orange-500" />
                    ) : (
                      <TrendingUp className="h-5 w-5 text-blue-500" />
                    )}
                    <div>
                      <div className="font-medium text-sm">{action.title}</div>
                      <div className="text-sm text-gray-600">{action.message}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={action.priority === 'high' ? 'destructive' : 'default'}>
                      {action.priority === 'high' ? 'Acil' : 'Önemli'}
                    </Badge>
                    <Button variant="outline" size="sm" asChild>
                      <Link to={`/app/rfqs/${action.rfqId}`}>
                        Görüntüle
                      </Link>
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* RFQ List - Takes more space */}
        <div className="xl:col-span-2">
          {rfqs && <DashboardRFQList rfqs={rfqs} isLoading={rfqsLoading} />}
        </div>

        {/* Sidebar - Activity Feed and Quick Actions */}
        <div className="xl:col-span-1 space-y-6">
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                Hızlı İşlemler
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full justify-start gap-2" variant="outline" asChild>
                <Link to="/app/rfqs/create">
                  <Plus className="h-4 w-4" />
                  Yeni RFQ Oluştur
                </Link>
              </Button>
              <Button className="w-full justify-start gap-2" variant="outline" asChild>
                <Link to="/app/suppliers">
                  <TrendingUp className="h-4 w-4" />
                  Tedarikçi Bul
                </Link>
              </Button>
              <Button className="w-full justify-start gap-2" variant="outline" asChild>
                <Link to="/app/offers">
                  <Eye className="h-4 w-4" />
                  Teklifleri İncele
                </Link>
              </Button>
              <Button className="w-full justify-start gap-2" variant="outline" asChild>
                <Link to="/app/notifications">
                  <Bell className="h-4 w-4" />
                  Bildirimler
                </Link>
              </Button>
            </CardContent>
          </Card>

          {/* Activity Feed */}
          {activities && <ActivityFeed activities={activities} />}
        </div>
      </div>
    </div>
  )
}
