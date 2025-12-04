import { Tag, Percent, Gift, Calendar } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

interface PromoCardProps {
    title: string
    competitor: string
    discountType: 'percent' | 'fixed' | 'free_ride'
    discountValue?: number
    validUntil?: string
    conditions?: string
    isActive: boolean
    targetAudience: 'driver' | 'rider' | 'unknown'
}

const discountIcons = {
    percent: Percent,
    fixed: Tag,
    free_ride: Gift,
}

export function PromoCard({
    title,
    competitor,
    discountType,
    discountValue,
    validUntil,
    conditions,
    isActive,
    targetAudience,
}: PromoCardProps) {
    const Icon = discountIcons[discountType]

    const formatDiscount = () => {
        switch (discountType) {
            case 'percent':
                return `${discountValue}% скидка`
            case 'fixed':
                return `S/${discountValue} скидка`
            case 'free_ride':
                return 'Бесплатная поездка'
            default:
                return 'Скидка'
        }
    }

    return (
        <Card className={cn('transition-opacity', !isActive && 'opacity-60')}>
            <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                        <div className="rounded-full bg-primary/10 p-2">
                            <Icon className="h-4 w-4 text-primary" />
                        </div>
                        <div>
                            <CardTitle className="text-base">{title}</CardTitle>
                            <p className="text-sm text-muted-foreground">{competitor}</p>
                        </div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                        <Badge variant={isActive ? 'success' : 'secondary'}>
                            {isActive ? 'Активна' : 'Истекла'}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                            {targetAudience === 'driver' ? 'Водители' : targetAudience === 'rider' ? 'Пассажиры' : 'Все'}
                        </Badge>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-3">
                    <div className="text-lg font-semibold text-primary">
                        {formatDiscount()}
                    </div>

                    {validUntil && (
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <Calendar className="h-4 w-4" />
                            До {format(new Date(validUntil), 'd MMMM yyyy', { locale: ru })}
                        </div>
                    )}

                    {conditions && (
                        <p className="text-sm text-muted-foreground line-clamp-2">
                            {conditions}
                        </p>
                    )}
                </div>
            </CardContent>
        </Card>
    )
}
