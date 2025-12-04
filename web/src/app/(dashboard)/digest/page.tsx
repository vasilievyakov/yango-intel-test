'use client'

import { useState } from 'react'
import { format, subDays, startOfWeek, endOfWeek, subWeeks } from 'date-fns'
import { ru } from 'date-fns/locale'
import ReactMarkdown from 'react-markdown'
import {
    FileText,
    Calendar,
    Download,
    RefreshCw,
    Copy,
    Check,
    ChevronDown,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'

// Mock digest data
const mockDigestContent = `# Дайджест за 8–15 января 2025

## Ключевые события

- **Didi снизила комиссию** с 18% до 15% — агрессивный ход для привлечения водителей
- **Uber запустил новую функцию безопасности** — автоматический SOS при длительной остановке
- **Cabify представила программу лояльности** — накопление баллов за поездки

## Новые релизы

### InDriver
- **iOS 5.12.3** (14 янв) — улучшена стабильность приложения, исправлены ошибки при приёме заказов
- **Android 5.12.2** (10 янв) — bugfix релиз

### Uber  
- **Android 4.521** (13 янв) — ⚠️ **Major**: новая функция безопасности с автоматическим SOS

### Didi
- **iOS 7.2.1** (12 янв) — обновлён интерфейс карты, добавлены новые способы оплаты

### Cabify
- **iOS 8.15.0** (8 янв) — ⚠️ **Major**: новая программа лояльности для пассажиров

## Изменения тарифов

| Конкурент | Параметр | Было | Стало | Изменение |
|-----------|----------|------|-------|-----------|
| Didi | Комиссия водителя | 18% | 15% | 🟢 -3% |

## Активные промоакции

| Конкурент | Акция | Скидка | Действует до |
|-----------|-------|--------|--------------|
| InDriver | 30% на первые 3 поездки | 30% | 31.01.2025 |
| Cabify | Бесплатная поездка до S/15 | S/15 | 15.02.2025 |
| Uber | Бонус S/100 за 20 поездок | S/100 | 20.01.2025 |

## Тренды в отзывах

### Негативные тренды 📉
- **InDriver**: рост жалоб на стабильность приложения (+20% за неделю)
- **Cabify**: проблемы с поддержкой и возвратами

### Позитивные тренды 📈
- **Uber**: хвалят новые функции безопасности
- **Didi**: положительная реакция на снижение комиссии

## Рекомендации для Yango

1. **Мониторинг Didi**: снижение комиссии может переманить водителей — рассмотреть ответные меры
2. **Функции безопасности**: Uber задаёт тренд — изучить возможность внедрения аналогичных функций
3. **Стабильность**: InDriver теряет лояльность из-за технических проблем — это возможность для привлечения их пользователей
`

const mockDigestHistory = [
    {
        id: '1',
        period_start: '2025-01-08',
        period_end: '2025-01-15',
        created_at: '2025-01-15T14:30:00Z',
        metadata: { releases_count: 5, tariff_changes_count: 1, active_promos_count: 3 },
    },
    {
        id: '2',
        period_start: '2025-01-01',
        period_end: '2025-01-07',
        created_at: '2025-01-07T16:00:00Z',
        metadata: { releases_count: 3, tariff_changes_count: 0, active_promos_count: 2 },
    },
    {
        id: '3',
        period_start: '2024-12-25',
        period_end: '2024-12-31',
        created_at: '2024-12-31T12:00:00Z',
        metadata: { releases_count: 2, tariff_changes_count: 2, active_promos_count: 4 },
    },
]

export default function DigestPage() {
    const [period, setPeriod] = useState<'week' | 'month'>('week')
    const [isGenerating, setIsGenerating] = useState(false)
    const [generatedDigest, setGeneratedDigest] = useState<string | null>(mockDigestContent)
    const [copied, setCopied] = useState(false)
    const [selectedHistoryId, setSelectedHistoryId] = useState<string | null>(null)

    const today = new Date()
    const weekStart = startOfWeek(today, { weekStartsOn: 1 })
    const weekEnd = endOfWeek(today, { weekStartsOn: 1 })
    const lastWeekStart = startOfWeek(subWeeks(today, 1), { weekStartsOn: 1 })
    const lastWeekEnd = endOfWeek(subWeeks(today, 1), { weekStartsOn: 1 })

    const handleGenerate = async () => {
        setIsGenerating(true)
        // Имитация генерации
        await new Promise((resolve) => setTimeout(resolve, 2000))
        setGeneratedDigest(mockDigestContent)
        setIsGenerating(false)
    }

    const handleCopy = async () => {
        if (generatedDigest) {
            await navigator.clipboard.writeText(generatedDigest)
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
        }
    }

    const handleExport = (format: 'markdown' | 'pdf') => {
        if (!generatedDigest) return

        if (format === 'markdown') {
            const blob = new Blob([generatedDigest], { type: 'text/markdown' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `digest-${format}-${new Date().toISOString().split('T')[0]}.md`
            a.click()
            URL.revokeObjectURL(url)
        }
        // PDF export would require additional library
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold tracking-tight">Дайджест</h1>
                <p className="text-muted-foreground">
                    Автоматическая генерация отчётов с помощью AI
                </p>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Generation Panel */}
                <div className="lg:col-span-1 space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Новый дайджест</CardTitle>
                            <CardDescription>
                                Выберите период и сгенерируйте отчёт
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Период</label>
                                <Select
                                    value={period}
                                    onValueChange={(v) => setPeriod(v as 'week' | 'month')}
                                >
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="week">Неделя</SelectItem>
                                        <SelectItem value="month">Месяц</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="p-3 rounded-lg bg-muted/50 text-sm">
                                <div className="flex items-center gap-2 text-muted-foreground mb-1">
                                    <Calendar className="h-4 w-4" />
                                    <span>Период отчёта:</span>
                                </div>
                                <p className="font-medium">
                                    {format(lastWeekStart, 'd MMM', { locale: ru })} —{' '}
                                    {format(lastWeekEnd, 'd MMM yyyy', { locale: ru })}
                                </p>
                            </div>

                            <Button
                                onClick={handleGenerate}
                                disabled={isGenerating}
                                className="w-full"
                            >
                                {isGenerating ? (
                                    <>
                                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                                        Генерация...
                                    </>
                                ) : (
                                    <>
                                        <FileText className="h-4 w-4 mr-2" />
                                        Сгенерировать
                                    </>
                                )}
                            </Button>
                        </CardContent>
                    </Card>

                    {/* History */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">История</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            {mockDigestHistory.map((digest) => (
                                <button
                                    key={digest.id}
                                    onClick={() => setSelectedHistoryId(digest.id)}
                                    className={`w-full p-3 rounded-lg text-left transition-colors ${
                                        selectedHistoryId === digest.id
                                            ? 'bg-primary/10 border border-primary'
                                            : 'bg-muted/50 hover:bg-muted'
                                    }`}
                                >
                                    <div className="font-medium text-sm">
                                        {format(new Date(digest.period_start), 'd MMM', {
                                            locale: ru,
                                        })}{' '}
                                        —{' '}
                                        {format(new Date(digest.period_end), 'd MMM', {
                                            locale: ru,
                                        })}
                                    </div>
                                    <div className="text-xs text-muted-foreground mt-1">
                                        {digest.metadata.releases_count} релизов •{' '}
                                        {digest.metadata.tariff_changes_count} изм. тарифов •{' '}
                                        {digest.metadata.active_promos_count} промо
                                    </div>
                                </button>
                            ))}
                        </CardContent>
                    </Card>
                </div>

                {/* Digest Content */}
                <div className="lg:col-span-2">
                    <Card className="h-full">
                        <CardHeader className="flex flex-row items-center justify-between">
                            <div>
                                <CardTitle className="text-lg">Предпросмотр</CardTitle>
                                <CardDescription>
                                    Отредактируйте или экспортируйте дайджест
                                </CardDescription>
                            </div>
                            {generatedDigest && (
                                <div className="flex gap-2">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={handleCopy}
                                    >
                                        {copied ? (
                                            <Check className="h-4 w-4 mr-1" />
                                        ) : (
                                            <Copy className="h-4 w-4 mr-1" />
                                        )}
                                        {copied ? 'Скопировано' : 'Копировать'}
                                    </Button>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => handleExport('markdown')}
                                    >
                                        <Download className="h-4 w-4 mr-1" />
                                        .md
                                    </Button>
                                </div>
                            )}
                        </CardHeader>
                        <CardContent>
                            {isGenerating ? (
                                <div className="space-y-4">
                                    <Skeleton className="h-8 w-3/4" />
                                    <Skeleton className="h-4 w-full" />
                                    <Skeleton className="h-4 w-full" />
                                    <Skeleton className="h-4 w-2/3" />
                                    <Skeleton className="h-6 w-1/2 mt-4" />
                                    <Skeleton className="h-4 w-full" />
                                    <Skeleton className="h-4 w-full" />
                                </div>
                            ) : generatedDigest ? (
                                <div className="prose prose-sm dark:prose-invert max-w-none">
                                    <ReactMarkdown
                                        components={{
                                            h1: ({ children }) => (
                                                <h1 className="text-xl font-bold mt-0 mb-4 pb-2 border-b">
                                                    {children}
                                                </h1>
                                            ),
                                            h2: ({ children }) => (
                                                <h2 className="text-lg font-semibold mt-6 mb-3">
                                                    {children}
                                                </h2>
                                            ),
                                            h3: ({ children }) => (
                                                <h3 className="text-base font-medium mt-4 mb-2">
                                                    {children}
                                                </h3>
                                            ),
                                            ul: ({ children }) => (
                                                <ul className="list-disc pl-5 space-y-1 my-2">
                                                    {children}
                                                </ul>
                                            ),
                                            li: ({ children }) => (
                                                <li className="text-sm">{children}</li>
                                            ),
                                            table: ({ children }) => (
                                                <div className="overflow-x-auto my-4">
                                                    <table className="w-full text-sm border-collapse">
                                                        {children}
                                                    </table>
                                                </div>
                                            ),
                                            thead: ({ children }) => (
                                                <thead className="bg-muted/50">{children}</thead>
                                            ),
                                            th: ({ children }) => (
                                                <th className="border px-3 py-2 text-left font-medium">
                                                    {children}
                                                </th>
                                            ),
                                            td: ({ children }) => (
                                                <td className="border px-3 py-2">{children}</td>
                                            ),
                                            strong: ({ children }) => (
                                                <strong className="font-semibold">{children}</strong>
                                            ),
                                            p: ({ children }) => (
                                                <p className="text-sm my-2">{children}</p>
                                            ),
                                        }}
                                    >
                                        {generatedDigest}
                                    </ReactMarkdown>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center justify-center py-12 text-center">
                                    <FileText className="h-12 w-12 text-muted-foreground/50 mb-4" />
                                    <p className="text-muted-foreground">
                                        Выберите период и нажмите &quot;Сгенерировать&quot;
                                    </p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    )
}

