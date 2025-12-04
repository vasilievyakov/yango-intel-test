'use client'

import { Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ComparisonTable } from '@/components/tariffs/ComparisonTable'

// Mock data for demo purposes
const mockDriverData = [
    { competitor: 'InDriver', commission_rate: 10, signup_bonus: 150, referral_bonus: 30 },
    { competitor: 'Uber', commission_rate: 25, signup_bonus: 200, referral_bonus: 50 },
    { competitor: 'Didi', commission_rate: 15, signup_bonus: 180, referral_bonus: 40 },
    { competitor: 'Cabify', commission_rate: 20, signup_bonus: 100, referral_bonus: 25 },
]

const mockRiderData = [
    { competitor: 'InDriver', base_fare: 3.5, per_km_rate: 1.2, per_min_rate: 0.3 },
    { competitor: 'Uber', base_fare: 4.5, per_km_rate: 1.8, per_min_rate: 0.4 },
    { competitor: 'Didi', base_fare: 3.8, per_km_rate: 1.4, per_min_rate: 0.35 },
    { competitor: 'Cabify', base_fare: 5.0, per_km_rate: 2.0, per_min_rate: 0.45 },
]

const driverColumns = [
    { key: 'competitor', label: 'Конкурент', sortable: false },
    {
        key: 'commission_rate',
        label: 'Комиссия',
        format: (v: number) => `${v}%`,
        highlight: 'min' as const,
    },
    {
        key: 'signup_bonus',
        label: 'Бонус регистрации',
        format: (v: number) => `S/${v}`,
        highlight: 'max' as const,
    },
    {
        key: 'referral_bonus',
        label: 'Реферальный бонус',
        format: (v: number) => `S/${v}`,
        highlight: 'max' as const,
    },
]

const riderColumns = [
    { key: 'competitor', label: 'Конкурент', sortable: false },
    {
        key: 'base_fare',
        label: 'Базовый тариф',
        format: (v: number) => `S/${v.toFixed(2)}`,
        highlight: 'min' as const,
    },
    {
        key: 'per_km_rate',
        label: 'За км',
        format: (v: number) => `S/${v.toFixed(2)}`,
        highlight: 'min' as const,
    },
    {
        key: 'per_min_rate',
        label: 'За минуту',
        format: (v: number) => `S/${v.toFixed(2)}`,
        highlight: 'min' as const,
    },
]

function exportToCSV(data: any[], filename: string) {
    const headers = Object.keys(data[0]).join(',')
    const rows = data.map(row => Object.values(row).join(','))
    const csv = [headers, ...rows].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
}

export default function TariffsPage() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Сравнение тарифов</h1>
                    <p className="text-muted-foreground">
                        Актуальные данные по всем конкурентам
                    </p>
                </div>
                <Button
                    variant="outline"
                    onClick={() => exportToCSV(mockDriverData, 'tariffs.csv')}
                >
                    <Download className="h-4 w-4 mr-2" />
                    Экспорт CSV
                </Button>
            </div>

            <Tabs defaultValue="driver" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="driver">Водители</TabsTrigger>
                    <TabsTrigger value="rider">Пассажиры</TabsTrigger>
                </TabsList>

                <TabsContent value="driver">
                    <ComparisonTable data={mockDriverData} columns={driverColumns} />
                    <p className="text-sm text-muted-foreground mt-3">
                        <span className="text-green-600">●</span> Лучшее значение {' '}
                        <span className="text-red-600">●</span> Худшее значение
                    </p>
                </TabsContent>

                <TabsContent value="rider">
                    <ComparisonTable data={mockRiderData} columns={riderColumns} />
                    <p className="text-sm text-muted-foreground mt-3">
                        <span className="text-green-600">●</span> Лучшее значение {' '}
                        <span className="text-red-600">●</span> Худшее значение
                    </p>
                </TabsContent>
            </Tabs>
        </div>
    )
}
