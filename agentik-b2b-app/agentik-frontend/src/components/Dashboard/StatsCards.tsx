import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  FileText, 
  Users, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  DollarSign,
  PieChart
} from 'lucide-react'

interface StatsCardsProps {
  stats: {
    totalRFQs: number
    pendingRFQs: number
    completedRFQs: number
    totalOffers: number
    avgResponseTime: string
    activeSuppliers: number
    totalBudget?: number
    savedAmount?: number
  }
}

export default function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Total RFQs */}
      <Card className="relative overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Toplam RFQ</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.totalRFQs}</div>
          <p className="text-xs text-muted-foreground">
            Son 30 günde oluşturulan
          </p>
          <div className="absolute bottom-0 right-0 w-16 h-16 bg-blue-500 opacity-10 rounded-full translate-x-8 translate-y-8"></div>
        </CardContent>
      </Card>

      {/* Pending RFQs */}
      <Card className="relative overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Bekleyen RFQ</CardTitle>
          <Clock className="h-4 w-4 text-orange-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-orange-600">
            {stats.pendingRFQs}
          </div>
          <p className="text-xs text-muted-foreground">
            Teklif bekleyen RFQ sayısı
          </p>
          <div className="absolute bottom-0 right-0 w-16 h-16 bg-orange-500 opacity-10 rounded-full translate-x-8 translate-y-8"></div>
        </CardContent>
      </Card>

      {/* Total Offers */}
      <Card className="relative overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Toplam Teklif</CardTitle>
          <TrendingUp className="h-4 w-4 text-blue-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-blue-600">
            {stats.totalOffers}
          </div>
          <p className="text-xs text-muted-foreground">
            Alınan teklif sayısı
          </p>
          <div className="absolute bottom-0 right-0 w-16 h-16 bg-blue-500 opacity-10 rounded-full translate-x-8 translate-y-8"></div>
        </CardContent>
      </Card>

      {/* Active Suppliers */}
      <Card className="relative overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Aktif Tedarikçi</CardTitle>
          <Users className="h-4 w-4 text-indigo-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-indigo-600">
            {stats.activeSuppliers}
          </div>
          <p className="text-xs text-muted-foreground">
            Bu ay aktif tedarikçi
          </p>
          <div className="absolute bottom-0 right-0 w-16 h-16 bg-indigo-500 opacity-10 rounded-full translate-x-8 translate-y-8"></div>
        </CardContent>
      </Card>

      {/* Completed RFQs */}
      <Card className="relative overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Tamamlanan RFQ</CardTitle>
          <CheckCircle className="h-4 w-4 text-green-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-green-600">
            {stats.completedRFQs}
          </div>
          <p className="text-xs text-muted-foreground">
            Başarıyla tamamlanan
          </p>
          <div className="absolute bottom-0 right-0 w-16 h-16 bg-green-500 opacity-10 rounded-full translate-x-8 translate-y-8"></div>
        </CardContent>
      </Card>

      {/* Average Response Time */}
      <Card className="relative overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Ortalama Yanıt</CardTitle>
          <AlertCircle className="h-4 w-4 text-purple-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-purple-600">
            {stats.avgResponseTime}
          </div>
          <p className="text-xs text-muted-foreground">
            Ortalama yanıt süresi
          </p>
          <div className="absolute bottom-0 right-0 w-16 h-16 bg-purple-500 opacity-10 rounded-full translate-x-8 translate-y-8"></div>
        </CardContent>
      </Card>

      {/* Total Budget */}
      {stats.totalBudget && (
        <Card className="relative overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Toplam Bütçe</CardTitle>
            <DollarSign className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-600">
              {(stats.totalBudget / 1000000).toFixed(1)}M ₺
            </div>
            <p className="text-xs text-muted-foreground">
              RFQ toplam bütçesi
            </p>
            <div className="absolute bottom-0 right-0 w-16 h-16 bg-emerald-500 opacity-10 rounded-full translate-x-8 translate-y-8"></div>
          </CardContent>
        </Card>
      )}

      {/* Saved Amount */}
      {stats.savedAmount && (
        <Card className="relative overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tasarruf Edilen</CardTitle>
            <PieChart className="h-4 w-4 text-teal-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-teal-600">
              {(stats.savedAmount / 1000).toFixed(0)}K ₺
            </div>
            <p className="text-xs text-muted-foreground">
              RFQ süreciyle tasarruf
            </p>
            <div className="absolute bottom-0 right-0 w-16 h-16 bg-teal-500 opacity-10 rounded-full translate-x-8 translate-y-8"></div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
