'use client'

import { useState } from 'react'
import { ReviewList } from '@/components/reviews/ReviewList'
import { SentimentChart } from '@/components/reviews/SentimentChart'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { Card, CardContent } from '@/components/ui/card'

// Mock data
const mockCompetitors = [
    { id: '1', name: 'InDriver' },
    { id: '2', name: 'Uber' },
    { id: '3', name: 'Didi' },
    { id: '4', name: 'Cabify' },
]

const mockReviews = [
    {
        id: '1',
        competitor: 'Uber',
        competitorId: '2',
        platform: 'ios' as const,
        author: 'Maria G.',
        rating: 5,
        text: 'Отлично! Водитель приехал вовремя, машина чистая',
        reviewDate: '2025-01-14T10:00:00Z',
        role: 'rider' as const,
        sentiment: 'positive' as const,
        categories: ['driver_behavior'],
    },
    {
        id: '2',
        competitor: 'InDriver',
        competitorId: '1',
        platform: 'android' as const,
        author: 'Pedro L.',
        rating: 2,
        text: 'Приложение постоянно вылетает, невозможно пользоваться',
        reviewDate: '2025-01-13T15:30:00Z',
        role: 'driver' as const,
        sentiment: 'negative' as const,
        categories: ['app_stability'],
    },
    {
        id: '3',
        competitor: 'Didi',
        competitorId: '3',
        platform: 'ios' as const,
        rating: 4,
        text: 'Хорошие цены, но долго ждать машину',
        reviewDate: '2025-01-12T08:00:00Z',
        role: 'rider' as const,
        sentiment: 'neutral' as const,
        categories: ['pricing', 'wait_time'],
    },
    {
        id: '4',
        competitor: 'Cabify',
        competitorId: '4',
        platform: 'android' as const,
        author: 'Ana R.',
        rating: 1,
        text: 'Ужасная поддержка! Не могу получить возврат за отменённую поездку уже месяц',
        reviewDate: '2025-01-11T12:00:00Z',
        role: 'rider' as const,
        sentiment: 'negative' as const,
        categories: ['support', 'payment'],
    },
    {
        id: '5',
        competitor: 'Uber',
        competitorId: '2',
        platform: 'android' as const,
        author: 'Carlos M.',
        rating: 5,
        text: 'Лучшее приложение для водителей, удобный интерфейс',
        reviewDate: '2025-01-10T09:00:00Z',
        role: 'driver' as const,
        sentiment: 'positive' as const,
        categories: ['other'],
    },
]

const mockSentimentData = [
    { competitor: 'Uber', positive: 45, neutral: 30, negative: 25, total: 127 },
    { competitor: 'InDriver', positive: 35, neutral: 25, negative: 40, total: 98 },
    { competitor: 'Didi', positive: 50, neutral: 35, negative: 15, total: 84 },
    { competitor: 'Cabify', positive: 40, neutral: 20, negative: 40, total: 62 },
]

export default function ReviewsPage() {
    const [selectedCompetitor, setSelectedCompetitor] = useState('all')
    const [selectedPlatform, setSelectedPlatform] = useState('all')
    const [selectedRole, setSelectedRole] = useState('all')
    const [selectedSentiment, setSelectedSentiment] = useState('all')

    const filteredReviews = mockReviews.filter((review) => {
        if (selectedCompetitor !== 'all' && review.competitorId !== selectedCompetitor) return false
        if (selectedPlatform !== 'all' && review.platform !== selectedPlatform) return false
        if (selectedRole !== 'all' && review.role !== selectedRole) return false
        if (selectedSentiment !== 'all' && review.sentiment !== selectedSentiment) return false
        return true
    })

    const totalReviews = mockSentimentData.reduce((sum, d) => sum + d.total, 0)

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold tracking-tight">Отзывы</h1>
                <p className="text-muted-foreground">
                    Анализ отзывов пользователей и водителей
                </p>
            </div>

            {/* Stats */}
            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardContent className="pt-6">
                        <div className="text-2xl font-bold">{totalReviews}</div>
                        <p className="text-sm text-muted-foreground">Всего отзывов</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="text-2xl font-bold text-green-600">
                            {Math.round(mockSentimentData.reduce((sum, d) => sum + d.positive, 0) / totalReviews * 100)}%
                        </div>
                        <p className="text-sm text-muted-foreground">Позитивных</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="text-2xl font-bold text-red-600">
                            {Math.round(mockSentimentData.reduce((sum, d) => sum + d.negative, 0) / totalReviews * 100)}%
                        </div>
                        <p className="text-sm text-muted-foreground">Негативных</p>
                    </CardContent>
                </Card>
            </div>

            {/* Sentiment Chart */}
            <SentimentChart data={mockSentimentData} />

            {/* Filters */}
            <div className="flex flex-wrap gap-4">
                <Select value={selectedCompetitor} onValueChange={setSelectedCompetitor}>
                    <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Конкурент" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">Все</SelectItem>
                        {mockCompetitors.map((c) => (
                            <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>

                <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                    <SelectTrigger className="w-[150px]">
                        <SelectValue placeholder="Платформа" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">Все</SelectItem>
                        <SelectItem value="ios">iOS</SelectItem>
                        <SelectItem value="android">Android</SelectItem>
                    </SelectContent>
                </Select>

                <Select value={selectedRole} onValueChange={setSelectedRole}>
                    <SelectTrigger className="w-[150px]">
                        <SelectValue placeholder="Роль" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">Все</SelectItem>
                        <SelectItem value="driver">Водители</SelectItem>
                        <SelectItem value="rider">Пассажиры</SelectItem>
                    </SelectContent>
                </Select>

                <Select value={selectedSentiment} onValueChange={setSelectedSentiment}>
                    <SelectTrigger className="w-[150px]">
                        <SelectValue placeholder="Тональность" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">Все</SelectItem>
                        <SelectItem value="positive">Позитивные</SelectItem>
                        <SelectItem value="neutral">Нейтральные</SelectItem>
                        <SelectItem value="negative">Негативные</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            {/* Review List */}
            <ReviewList reviews={filteredReviews} />
        </div>
    )
}
