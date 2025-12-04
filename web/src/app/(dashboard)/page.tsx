import { Clock, Smartphone, MessageSquare, Tag, TrendingUp } from 'lucide-react'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { HealthStatus } from '@/components/dashboard/HealthStatus'
import { RecentActivity } from '@/components/dashboard/RecentActivity'

// Mock data for demo purposes - will be replaced with API calls
const mockSummary = {
    last_collection: new Date().toISOString(),
    new_releases_week: 5,
    new_reviews_week: 127,
    active_promos: { indriver: 2, uber: 1, didi: 3, cabify: 1 },
    health_status: 'healthy' as const,
    tariff_changes_week: 2,
}

const mockActivities = [
    {
        id: '1',
        type: 'release' as const,
        competitor: 'InDriver',
        description: 'Версия 5.12.3 — улучшена стабильность',
        platform: 'ios' as const,
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    },
    {
        id: '2',
        type: 'tariff_change' as const,
        competitor: 'Didi',
        description: 'Комиссия снижена с 18% до 15%',
        timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    },
    {
        id: '3',
        type: 'release' as const,
        competitor: 'Uber',
        description: 'Версия 4.521 — новая функция безопасности',
        platform: 'android' as const,
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    },
]

export default function DashboardPage() {
    const totalActivePromos = Object.values(mockSummary.active_promos).reduce((a, b) => a + b, 0)

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold tracking-tight">Обзор</h1>
                <p className="text-muted-foreground">
                    Ключевые метрики и статус системы
                </p>
            </div>

            {/* Stats Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <StatsCard
                    title="Последний сбор"
                    value="2ч назад"
                    icon={Clock}
                    description="Все источники"
                />
                <StatsCard
                    title="Новых релизов"
                    value={mockSummary.new_releases_week}
                    icon={Smartphone}
                    description="за последние 7 дней"
                    trend={{ value: 25, isPositive: true }}
                />
                <StatsCard
                    title="Новых отзывов"
                    value={mockSummary.new_reviews_week}
                    icon={MessageSquare}
                    description="за последние 7 дней"
                    trend={{ value: 12, isPositive: false }}
                />
                <StatsCard
                    title="Активных промо"
                    value={totalActivePromos}
                    icon={Tag}
                    description="у всех конкурентов"
                />
            </div>

            {/* Second Row */}
            <div className="grid gap-4 md:grid-cols-2">
                <HealthStatus
                    status={mockSummary.health_status}
                    lastCollection={mockSummary.last_collection}
                />
                <StatsCard
                    title="Изменений тарифов"
                    value={mockSummary.tariff_changes_week}
                    icon={TrendingUp}
                    description="за последние 7 дней"
                    className="h-full"
                />
            </div>

            {/* Recent Activity */}
            <RecentActivity activities={mockActivities} />
        </div>
    )
}
