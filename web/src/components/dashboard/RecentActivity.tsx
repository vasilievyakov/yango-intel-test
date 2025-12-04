import { Smartphone, Apple, DollarSign } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'

interface ActivityItem {
    id: string
    type: 'release' | 'tariff_change'
    competitor: string
    description: string
    platform?: 'ios' | 'android'
    timestamp: string
}

interface RecentActivityProps {
    activities: ActivityItem[]
    className?: string
}

export function RecentActivity({ activities, className }: RecentActivityProps) {
    return (
        <Card className={className}>
            <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                    Последняя активность
                </CardTitle>
            </CardHeader>
            <CardContent>
                {activities.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-4">
                        Нет недавней активности
                    </p>
                ) : (
                    <div className="space-y-4">
                        {activities.map((activity) => (
                            <div key={activity.id} className="flex items-start gap-3">
                                <div className="rounded-full bg-muted p-2">
                                    {activity.type === 'release' ? (
                                        activity.platform === 'ios' ? (
                                            <Apple className="h-4 w-4" />
                                        ) : (
                                            <Smartphone className="h-4 w-4" />
                                        )
                                    ) : (
                                        <DollarSign className="h-4 w-4" />
                                    )}
                                </div>
                                <div className="flex-1 space-y-1">
                                    <div className="flex items-center gap-2">
                                        <span className="font-medium text-sm">{activity.competitor}</span>
                                        <Badge variant="secondary" className="text-xs">
                                            {activity.type === 'release' ? 'Релиз' : 'Тариф'}
                                        </Badge>
                                    </div>
                                    <p className="text-sm text-muted-foreground">{activity.description}</p>
                                    <p className="text-xs text-muted-foreground">
                                        {formatDistanceToNow(new Date(activity.timestamp), {
                                            addSuffix: true,
                                            locale: ru,
                                        })}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
