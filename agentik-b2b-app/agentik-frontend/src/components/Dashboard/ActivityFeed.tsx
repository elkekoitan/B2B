import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  FileText, 
  MessageCircle, 
  TrendingUp, 
  Bell, 
  CheckCircle,
  AlertTriangle
} from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'
import { tr } from 'date-fns/locale'

interface ActivityFeedProps {
  activities: Array<{
    id: string
    type: 'rfq_created' | 'offer_received' | 'rfq_closed' | 'award_made' | 'message' | 'system'
    title: string
    description: string
    timestamp: string
    metadata?: Record<string, any>
  }>
}

const activityIcons = {
  rfq_created: FileText,
  offer_received: TrendingUp,
  rfq_closed: CheckCircle,
  award_made: AlertTriangle,
  message: MessageCircle,
  system: Bell
}

const activityColors = {
  rfq_created: 'text-blue-500',
  offer_received: 'text-green-500',
  rfq_closed: 'text-gray-500',
  award_made: 'text-purple-500',
  message: 'text-orange-500',
  system: 'text-yellow-500'
}

export default function ActivityFeed({ activities }: ActivityFeedProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Son Aktiviteler</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {activities.length === 0 ? (
          <div className="text-center py-6 text-gray-500">
            <Bell className="mx-auto h-12 w-12 text-gray-300 mb-4" />
            <p>Henüz aktivite bulunmamaktadır.</p>
          </div>
        ) : (
          activities.map((activity) => {
            const Icon = activityIcons[activity.type]
            const colorClass = activityColors[activity.type]
            
            return (
              <div key={activity.id} className="flex items-start gap-3 pb-4 border-b last:border-b-0">
                <div className={`p-2 rounded-full bg-gray-100 ${colorClass}`}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex-1">
                  <div className="font-medium text-sm">{activity.title}</div>
                  <div className="text-sm text-gray-600 mt-1">
                    {activity.description}
                  </div>
                  <div className="text-xs text-gray-400 mt-2">
                    {formatDistanceToNow(new Date(activity.timestamp), {
                      addSuffix: true,
                      locale: tr
                    })}
                  </div>
                </div>
              </div>
            )
          })
        )}
      </CardContent>
    </Card>
  )
}
