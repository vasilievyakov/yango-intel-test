'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface SentimentData {
    competitor: string
    positive: number
    neutral: number
    negative: number
    total: number
}

interface SentimentChartProps {
    data: SentimentData[]
    className?: string
}

export function SentimentChart({ data, className }: SentimentChartProps) {
    return (
        <Card className={className}>
            <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                    Распределение по тональности
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {data.map((item) => {
                        const positivePercent = item.total > 0 ? (item.positive / item.total) * 100 : 0
                        const neutralPercent = item.total > 0 ? (item.neutral / item.total) * 100 : 0
                        const negativePercent = item.total > 0 ? (item.negative / item.total) * 100 : 0

                        return (
                            <div key={item.competitor}>
                                <div className="flex items-center justify-between mb-1">
                                    <span className="text-sm font-medium">{item.competitor}</span>
                                    <span className="text-sm text-muted-foreground">{item.total} отзывов</span>
                                </div>
                                <div className="h-3 flex rounded-full overflow-hidden bg-muted">
                                    <div
                                        className="bg-green-500 transition-all"
                                        style={{ width: `${positivePercent}%` }}
                                    />
                                    <div
                                        className="bg-gray-400 transition-all"
                                        style={{ width: `${neutralPercent}%` }}
                                    />
                                    <div
                                        className="bg-red-500 transition-all"
                                        style={{ width: `${negativePercent}%` }}
                                    />
                                </div>
                                <div className="flex justify-between mt-1 text-xs text-muted-foreground">
                                    <span className="text-green-600">{Math.round(positivePercent)}% позитив</span>
                                    <span className="text-red-600">{Math.round(negativePercent)}% негатив</span>
                                </div>
                            </div>
                        )
                    })}
                </div>
            </CardContent>
        </Card>
    )
}
