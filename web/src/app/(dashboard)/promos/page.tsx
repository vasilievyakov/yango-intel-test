'use client'

import { useState } from 'react'
import { PromoCard } from '@/components/promos/PromoCard'
import { PromoFilters } from '@/components/promos/PromoFilters'

// Mock data
const mockCompetitors = [
    { id: '1', name: 'InDriver' },
    { id: '2', name: 'Uber' },
    { id: '3', name: 'Didi' },
    { id: '4', name: 'Cabify' },
]

const mockPromos = [
    {
        id: '1',
        title: '30% скидка на первые 3 поездки',
        competitor: 'InDriver',
        competitorId: '1',
        discountType: 'percent' as const,
        discountValue: 30,
        validUntil: '2025-01-31',
        conditions: 'Для новых пользователей',
        isActive: true,
        targetAudience: 'rider' as const,
    },
    {
        id: '2',
        title: 'Бесплатная поездка до S/15',
        competitor: 'Cabify',
        competitorId: '4',
        discountType: 'free_ride' as const,
        discountValue: 15,
        validUntil: '2025-02-15',
        conditions: 'При регистрации по промокоду CABIFY2025',
        isActive: true,
        targetAudience: 'rider' as const,
    },
    {
        id: '3',
        title: 'Бонус S/100 за первые 20 поездок',
        competitor: 'Uber',
        competitorId: '2',
        discountType: 'fixed' as const,
        discountValue: 100,
        validUntil: '2025-01-20',
        conditions: 'Для новых водителей',
        isActive: true,
        targetAudience: 'driver' as const,
    },
    {
        id: '4',
        title: '15% кешбэк',
        competitor: 'Didi',
        competitorId: '3',
        discountType: 'percent' as const,
        discountValue: 15,
        validUntil: '2024-12-31',
        conditions: 'На поездки по пятницам',
        isActive: false,
        targetAudience: 'rider' as const,
    },
]

export default function PromosPage() {
    const [selectedCompetitor, setSelectedCompetitor] = useState('all')
    const [activeOnly, setActiveOnly] = useState(true)
    const [targetAudience, setTargetAudience] = useState('all')

    const filteredPromos = mockPromos.filter((promo) => {
        if (selectedCompetitor !== 'all' && promo.competitorId !== selectedCompetitor) {
            return false
        }
        if (activeOnly && !promo.isActive) {
            return false
        }
        if (targetAudience !== 'all' && promo.targetAudience !== targetAudience) {
            return false
        }
        return true
    })

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold tracking-tight">Промоакции</h1>
                <p className="text-muted-foreground">
                    Текущие и прошедшие акции конкурентов
                </p>
            </div>

            <PromoFilters
                competitors={mockCompetitors}
                selectedCompetitor={selectedCompetitor}
                onCompetitorChange={setSelectedCompetitor}
                activeOnly={activeOnly}
                onActiveOnlyChange={setActiveOnly}
                targetAudience={targetAudience}
                onTargetAudienceChange={setTargetAudience}
            />

            {filteredPromos.length === 0 ? (
                <div className="text-center py-12">
                    <p className="text-muted-foreground">Нет промоакций по выбранным фильтрам</p>
                </div>
            ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {filteredPromos.map((promo) => (
                        <PromoCard
                            key={promo.id}
                            title={promo.title}
                            competitor={promo.competitor}
                            discountType={promo.discountType}
                            discountValue={promo.discountValue}
                            validUntil={promo.validUntil}
                            conditions={promo.conditions}
                            isActive={promo.isActive}
                            targetAudience={promo.targetAudience}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}
