'use client'

import { Star, ThumbsUp, ThumbsDown, Minus, Apple, Smartphone } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'

interface Review {
    id: string
    competitor: string
    platform: 'ios' | 'android'
    author?: string
    rating: number
    text?: string
    reviewDate: string
    role: 'driver' | 'rider' | 'unknown'
    sentiment: 'positive' | 'neutral' | 'negative'
    categories?: string[]
}

interface ReviewListProps {
    reviews: Review[]
    className?: string
}

const sentimentConfig = {
    positive: { icon: ThumbsUp, color: 'text-green-600', bg: 'bg-green-50' },
    neutral: { icon: Minus, color: 'text-gray-600', bg: 'bg-gray-50' },
    negative: { icon: ThumbsDown, color: 'text-red-600', bg: 'bg-red-50' },
}

const categoryLabels: Record<string, string> = {
    pricing: 'Цены',
    app_stability: 'Стабильность',
    driver_behavior: 'Поведение водителя',
    wait_time: 'Время ожидания',
    payment: 'Оплата',
    support: 'Поддержка',
    other: 'Другое',
}

export function ReviewList({ reviews, className }: ReviewListProps) {
    if (reviews.length === 0) {
        return (
            <div className="text-center py-12">
                <p className="text-muted-foreground">Нет отзывов по выбранным фильтрам</p>
            </div>
        )
    }

    return (
        <div className={cn('space-y-4', className)}>
            {reviews.map((review) => {
                const sentiment = sentimentConfig[review.sentiment]
                const SentimentIcon = sentiment.icon

                return (
                    <Card key={review.id}>
                        <CardContent className="pt-4">
                            <div className="flex items-start justify-between">
                                <div className="flex items-start gap-3">
                                    <div className={cn('rounded-full p-2', sentiment.bg)}>
                                        <SentimentIcon className={cn('h-4 w-4', sentiment.color)} />
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <span className="font-medium">{review.competitor}</span>
                                            {review.platform === 'ios' ? (
                                                <Apple className="h-4 w-4 text-muted-foreground" />
                                            ) : (
                                                <Smartphone className="h-4 w-4 text-muted-foreground" />
                                            )}
                                            <Badge variant="outline" className="text-xs">
                                                {review.role === 'driver' ? 'Водитель' : review.role === 'rider' ? 'Пассажир' : '—'}
                                            </Badge>
                                        </div>
                                        <div className="flex items-center gap-2 mt-1">
                                            <div className="flex items-center">
                                                {Array.from({ length: 5 }).map((_, i) => (
                                                    <Star
                                                        key={i}
                                                        className={cn(
                                                            'h-4 w-4',
                                                            i < review.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-200'
                                                        )}
                                                    />
                                                ))}
                                            </div>
                                            <span className="text-sm text-muted-foreground">
                                                {review.author || 'Аноним'}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <span className="text-sm text-muted-foreground">
                                    {formatDistanceToNow(new Date(review.reviewDate), { addSuffix: true, locale: ru })}
                                </span>
                            </div>

                            {review.text && (
                                <p className="mt-3 text-sm text-muted-foreground line-clamp-3">
                                    {review.text}
                                </p>
                            )}

                            {review.categories && review.categories.length > 0 && (
                                <div className="mt-3 flex flex-wrap gap-1">
                                    {review.categories.map((cat) => (
                                        <Badge key={cat} variant="secondary" className="text-xs">
                                            {categoryLabels[cat] || cat}
                                        </Badge>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                )
            })}
        </div>
    )
}
