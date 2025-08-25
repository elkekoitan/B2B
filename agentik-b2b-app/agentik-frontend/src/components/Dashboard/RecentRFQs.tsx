import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Calendar, ArrowRight } from 'lucide-react'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

interface RecentRFQsProps {
  rfqs: Array<{
    id: string
    title: string
    company: string
    status: 'draft' | 'published' | 'closed' | 'awarded'
    deadline: string
    offerCount: number
    createdAt: string
  }>
}

const statusLabels = {
  draft: { label: 'Taslak', variant: 'outline' as const },
  published: { label: 'Yayında', variant: 'info' as const },
  closed: { label: 'Kapalı', variant: 'secondary' as const },
  awarded: { label: 'İhale Edildi', variant: 'success' as const }
}

export default function RecentRFQs({ rfqs }: RecentRFQsProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Son RFQ'lar</CardTitle>
        <Button variant="ghost" size="sm" asChild>
          <Link to="/app/rfqs" className="flex items-center text-sm">
            Tümünü Gör
            <ArrowRight className="ml-1 h-4 w-4" />
          </Link>
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {rfqs.length === 0 ? (
          <div className="text-center py-6 text-gray-500">
            <p>Henüz RFQ oluşturmadınız.</p>
            <Button className="mt-2" asChild>
              <Link to="/app/rfqs/create">İlk RFQ'nizi Oluşturun</Link>
            </Button>
          </div>
        ) : (
          rfqs.map((rfq) => (
            <div key={rfq.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <Link 
                    to={`/app/rfqs/${rfq.id}`} 
                    className="font-medium hover:text-blue-600 transition-colors"
                  >
                    {rfq.title}
                  </Link>
                  <Badge variant={statusLabels[rfq.status].variant}>
                    {statusLabels[rfq.status].label}
                  </Badge>
                </div>
                <div className="text-sm text-gray-600 space-y-1">
                  <p className="font-medium">{rfq.company}</p>
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      Son Tarih: {format(new Date(rfq.deadline), 'dd MMM yyyy', { locale: tr })}
                    </span>
                    <span>{rfq.offerCount} teklif alındı</span>
                  </div>
                </div>
              </div>
              <Button variant="outline" size="sm" asChild>
                <Link to={`/app/rfqs/${rfq.id}`}>Detay</Link>
              </Button>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  )
}
