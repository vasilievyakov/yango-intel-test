'use client'

import { useState } from 'react'
import { ReleaseTimeline } from '@/components/releases/ReleaseTimeline'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'

// Mock data
const mockCompetitors = [
    { id: '1', name: 'InDriver' },
    { id: '2', name: 'Uber' },
    { id: '3', name: 'Didi' },
    { id: '4', name: 'Cabify' },
]

const mockReleases = [
    {
        id: '1',
        competitor: 'InDriver',
        competitorId: '1',
        platform: 'ios' as const,
        version: '5.12.3',
        releaseDate: '2025-01-14',
        releaseNotes: 'Улучшена стабильность приложения, исправлены ошибки при приёме заказов',
        categories: ['ux_ui', 'driver_exp'],
        significance: 'minor' as const,
    },
    {
        id: '2',
        competitor: 'Uber',
        competitorId: '2',
        platform: 'android' as const,
        version: '4.521',
        releaseDate: '2025-01-13',
        releaseNotes: 'Новая функция безопасности: автоматический SOS при длительной остановке',
        categories: ['safety'],
        significance: 'major' as const,
    },
    {
        id: '3',
        competitor: 'Didi',
        competitorId: '3',
        platform: 'ios' as const,
        version: '7.2.1',
        releaseDate: '2025-01-12',
        releaseNotes: 'Обновлён интерфейс карты, добавлены новые способы оплаты',
        categories: ['ux_ui', 'rider_exp'],
        significance: 'minor' as const,
    },
    {
        id: '4',
        competitor: 'InDriver',
        competitorId: '1',
        platform: 'android' as const,
        version: '5.12.2',
        releaseDate: '2025-01-10',
        releaseNotes: 'Исправлены ошибки',
        categories: ['other'],
        significance: 'bugfix' as const,
    },
    {
        id: '5',
        competitor: 'Cabify',
        competitorId: '4',
        platform: 'ios' as const,
        version: '8.15.0',
        releaseDate: '2025-01-08',
        releaseNotes: 'Новая программа лояльности для пассажиров',
        categories: ['promo', 'rider_exp'],
        significance: 'major' as const,
    },
]

const categories = [
    { id: 'pricing', name: 'Тарифы' },
    { id: 'ux_ui', name: 'UX/UI' },
    { id: 'safety', name: 'Безопасность' },
    { id: 'driver_exp', name: 'Водители' },
    { id: 'rider_exp', name: 'Пассажиры' },
    { id: 'promo', name: 'Промо' },
]

export default function ReleasesPage() {
    const [selectedCompetitor, setSelectedCompetitor] = useState('all')
    const [selectedPlatform, setSelectedPlatform] = useState('all')
    const [selectedCategory, setSelectedCategory] = useState('all')

    const filteredReleases = mockReleases.filter((release) => {
        if (selectedCompetitor !== 'all' && release.competitorId !== selectedCompetitor) {
            return false
        }
        if (selectedPlatform !== 'all' && release.platform !== selectedPlatform) {
            return false
        }
        if (selectedCategory !== 'all' && !release.categories?.includes(selectedCategory)) {
            return false
        }
        return true
    })

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold tracking-tight">Релизы приложений</h1>
                <p className="text-muted-foreground">
                    История обновлений приложений конкурентов
                </p>
            </div>

            <div className="flex flex-wrap gap-4">
                <Select value={selectedCompetitor} onValueChange={setSelectedCompetitor}>
                    <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Конкурент" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">Все конкуренты</SelectItem>
                        {mockCompetitors.map((c) => (
                            <SelectItem key={c.id} value={c.id}>
                                {c.name}
                            </SelectItem>
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

                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Категория" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">Все категории</SelectItem>
                        {categories.map((c) => (
                            <SelectItem key={c.id} value={c.id}>
                                {c.name}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
                <span className="flex items-center gap-1">
                    <span className="h-2 w-2 rounded-full bg-blue-500" /> Major
                </span>
                <span className="flex items-center gap-1">
                    <span className="h-2 w-2 rounded-full bg-green-500" /> Minor
                </span>
                <span className="flex items-center gap-1">
                    <span className="h-2 w-2 rounded-full bg-gray-400" /> Bugfix
                </span>
            </div>

            <ReleaseTimeline releases={filteredReleases} />
        </div>
    )
}
