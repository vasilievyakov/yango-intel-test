import { CheckCircle2, AlertCircle, XCircle, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'

interface HealthStatusProps {
    status: 'healthy' | 'warning' | 'error'
    lastCollection?: string
    className?: string
}

const statusConfig = {
    healthy: {
        icon: CheckCircle2,
        label: 'Система работает',
        color: 'text-green-600',
        bgColor: 'bg-green-50',
    },
    warning: {
        icon: AlertCircle,
        label: 'Есть проблемы',
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-50',
    },
    error: {
        icon: XCircle,
        label: 'Сбор не работает',
        color: 'text-red-600',
        bgColor: 'bg-red-50',
    },
}

export function HealthStatus({ status, lastCollection, className }: HealthStatusProps) {
    const config = statusConfig[status]
    const Icon = config.icon

    const lastCollectionText = lastCollection
        ? formatDistanceToNow(new Date(lastCollection), { addSuffix: true, locale: ru })
        : 'Никогда'

    return (
        <Card className={cn('', className)}>
            <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                    Статус системы
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className={cn('flex items-center gap-3 p-3 rounded-lg', config.bgColor)}>
                    <Icon className={cn('h-8 w-8', config.color)} />
                    <div>
                        <p className={cn('font-semibold', config.color)}>{config.label}</p>
                        <p className="text-sm text-muted-foreground flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            Последний сбор: {lastCollectionText}
                        </p>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}
