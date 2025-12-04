'use client'

import { useState, useEffect } from 'react'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'
import {
    Newspaper,
    Search,
    ExternalLink,
    RefreshCw,
    Filter,
    TrendingUp,
    TrendingDown,
    Minus,
    Globe,
    Calendar,
    Building2,
    Tag,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'

interface NewsItem {
    id: string
    title: string
    summary: string
    source_url: string
    source_name: string
    published_date: string
    competitors_mentioned: string[]
    topics: string[]
    sentiment: 'positive' | 'negative' | 'neutral'
    relevance_score: number
    search_query: string
    collected_at: string
}

interface NewsResponse {
    items: NewsItem[]
    total: number
    page: number
    pages: number
}

// Use local API proxy to avoid CORS issues
const API_URL = ''

const competitorColors: Record<string, string> = {
    uber: 'bg-black text-white',
    didi: 'bg-orange-500 text-white',
    indrive: 'bg-green-600 text-white',
    cabify: 'bg-purple-600 text-white',
    yango: 'bg-red-500 text-white',
    rappi: 'bg-orange-600 text-white',
    bolt: 'bg-green-500 text-white',
}

const topicLabels: Record<string, string> = {
    technology: 'Технологии',
    pricing: 'Цены',
    safety: 'Безопасность',
    drivers: 'Водители',
    promo: 'Промо',
    expansion: 'Расширение',
    regulation: 'Регулирование',
}

const sentimentIcons = {
    positive: { icon: TrendingUp, color: 'text-green-500' },
    negative: { icon: TrendingDown, color: 'text-red-500' },
    neutral: { icon: Minus, color: 'text-gray-500' },
}

export default function NewsPage() {
    const [news, setNews] = useState<NewsItem[]>([])
    const [loading, setLoading] = useState(true)
    const [searching, setSearching] = useState(false)
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedCompetitor, setSelectedCompetitor] = useState<string>('all')
    const [totalNews, setTotalNews] = useState(0)
    const [currentPage, setCurrentPage] = useState(1)
    const [totalPages, setTotalPages] = useState(1)
    const [error, setError] = useState<string | null>(null)

    const fetchNews = async (page = 1) => {
        setLoading(true)
        setError(null)
        try {
            const params = new URLSearchParams({
                page: page.toString(),
                limit: '20',
            })
            if (selectedCompetitor && selectedCompetitor !== 'all') {
                params.append('competitor', selectedCompetitor)
            }
            
            const response = await fetch(`${API_URL}/api/news?${params}`)
            if (!response.ok) throw new Error('Failed to fetch news')
            
            const data: NewsResponse = await response.json()
            setNews(data.items)
            setTotalNews(data.total)
            setCurrentPage(data.page)
            setTotalPages(data.pages)
        } catch (err) {
            setError('Ошибка загрузки новостей')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const handleSearch = async () => {
        if (!searchQuery.trim()) return
        
        setSearching(true)
        setError(null)
        try {
            const response = await fetch(`${API_URL}/api/news/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: searchQuery,
                    competitors: selectedCompetitor !== 'all' ? [selectedCompetitor] : undefined,
                    language: 'es',
                }),
            })
            
            if (!response.ok) throw new Error('Search failed')
            
            const data = await response.json()
            // Refresh the news list after search
            await fetchNews()
        } catch (err) {
            setError('Ошибка поиска')
            console.error(err)
        } finally {
            setSearching(false)
        }
    }

    useEffect(() => {
        fetchNews()
    }, [selectedCompetitor])

    const SentimentIcon = ({ sentiment }: { sentiment: 'positive' | 'negative' | 'neutral' }) => {
        const { icon: Icon, color } = sentimentIcons[sentiment]
        return <Icon className={`h-4 w-4 ${color}`} />
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold tracking-tight">Новости рынка</h1>
                <p className="text-muted-foreground">
                    Мониторинг новостей о конкурентах через Parallel AI
                </p>
            </div>

            {/* Search & Filters */}
            <Card>
                <CardContent className="pt-6">
                    <div className="flex flex-col sm:flex-row gap-4">
                        <div className="flex-1 flex gap-2">
                            <Input
                                placeholder="Поиск новостей (например: Uber promociones Lima)"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                className="flex-1"
                            />
                            <Button onClick={handleSearch} disabled={searching}>
                                {searching ? (
                                    <RefreshCw className="h-4 w-4 animate-spin" />
                                ) : (
                                    <Search className="h-4 w-4" />
                                )}
                            </Button>
                        </div>
                        
                        <Select value={selectedCompetitor} onValueChange={setSelectedCompetitor}>
                            <SelectTrigger className="w-[180px]">
                                <Filter className="h-4 w-4 mr-2" />
                                <SelectValue placeholder="Конкурент" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Все конкуренты</SelectItem>
                                <SelectItem value="uber">Uber</SelectItem>
                                <SelectItem value="didi">DiDi</SelectItem>
                                <SelectItem value="indrive">inDrive</SelectItem>
                                <SelectItem value="cabify">Cabify</SelectItem>
                                <SelectItem value="yango">Yango</SelectItem>
                                <SelectItem value="rappi">Rappi</SelectItem>
                                <SelectItem value="bolt">Bolt</SelectItem>
                            </SelectContent>
                        </Select>

                        <Button variant="outline" onClick={() => fetchNews()}>
                            <RefreshCw className="h-4 w-4 mr-2" />
                            Обновить
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Stats */}
            <div className="grid gap-4 md:grid-cols-4">
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-2">
                            <Newspaper className="h-5 w-5 text-blue-500" />
                            <div>
                                <p className="text-2xl font-bold">{totalNews}</p>
                                <p className="text-xs text-muted-foreground">всего новостей</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-2">
                            <TrendingUp className="h-5 w-5 text-green-500" />
                            <div>
                                <p className="text-2xl font-bold">
                                    {news.filter(n => n.sentiment === 'positive').length}
                                </p>
                                <p className="text-xs text-muted-foreground">позитивных</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-2">
                            <TrendingDown className="h-5 w-5 text-red-500" />
                            <div>
                                <p className="text-2xl font-bold">
                                    {news.filter(n => n.sentiment === 'negative').length}
                                </p>
                                <p className="text-xs text-muted-foreground">негативных</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-2">
                            <Building2 className="h-5 w-5 text-purple-500" />
                            <div>
                                <p className="text-2xl font-bold">
                                    {new Set(news.flatMap(n => n.competitors_mentioned)).size}
                                </p>
                                <p className="text-xs text-muted-foreground">конкурентов</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Error */}
            {error && (
                <Card className="border-red-200 bg-red-50">
                    <CardContent className="pt-6 text-red-600">
                        {error}
                    </CardContent>
                </Card>
            )}

            {/* News List */}
            <div className="space-y-4">
                {loading ? (
                    Array.from({ length: 5 }).map((_, i) => (
                        <Card key={i}>
                            <CardContent className="pt-6">
                                <div className="space-y-3">
                                    <Skeleton className="h-6 w-3/4" />
                                    <Skeleton className="h-4 w-full" />
                                    <Skeleton className="h-4 w-2/3" />
                                    <div className="flex gap-2">
                                        <Skeleton className="h-6 w-16" />
                                        <Skeleton className="h-6 w-20" />
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ))
                ) : news.length === 0 ? (
                    <Card>
                        <CardContent className="pt-6">
                            <div className="text-center py-12">
                                <Newspaper className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
                                <p className="text-muted-foreground">
                                    Новостей пока нет. Выполните поиск, чтобы добавить.
                                </p>
                            </div>
                        </CardContent>
                    </Card>
                ) : (
                    news.map((item) => (
                        <Card key={item.id} className="hover:shadow-md transition-shadow">
                            <CardContent className="pt-6">
                                <div className="space-y-3">
                                    {/* Header */}
                                    <div className="flex items-start justify-between gap-4">
                                        <h3 className="font-semibold text-lg leading-tight">
                                            {item.title}
                                        </h3>
                                        <SentimentIcon sentiment={item.sentiment} />
                                    </div>

                                    {/* Summary */}
                                    <p className="text-sm text-muted-foreground line-clamp-3">
                                        {item.summary}
                                    </p>

                                    {/* Competitors & Topics */}
                                    <div className="flex flex-wrap gap-2">
                                        {item.competitors_mentioned.map((comp) => (
                                            <Badge
                                                key={comp}
                                                className={competitorColors[comp] || 'bg-gray-500'}
                                            >
                                                {comp.charAt(0).toUpperCase() + comp.slice(1)}
                                            </Badge>
                                        ))}
                                        {item.topics.map((topic) => (
                                            <Badge key={topic} variant="outline">
                                                {topicLabels[topic] || topic}
                                            </Badge>
                                        ))}
                                    </div>

                                    {/* Meta */}
                                    <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground pt-2 border-t">
                                        <div className="flex items-center gap-1">
                                            <Globe className="h-3 w-3" />
                                            <span>{item.source_name}</span>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Calendar className="h-3 w-3" />
                                            <span>
                                                {item.published_date ? 
                                                    format(new Date(item.published_date), 'd MMM yyyy', { locale: ru }) :
                                                    'Дата неизвестна'
                                                }
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Tag className="h-3 w-3" />
                                            <span>Релевантность: {Math.round(item.relevance_score * 100)}%</span>
                                        </div>
                                        <a
                                            href={item.source_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="flex items-center gap-1 text-primary hover:underline ml-auto"
                                        >
                                            <ExternalLink className="h-3 w-3" />
                                            <span>Источник</span>
                                        </a>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ))
                )}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex justify-center gap-2">
                    <Button
                        variant="outline"
                        disabled={currentPage <= 1}
                        onClick={() => fetchNews(currentPage - 1)}
                    >
                        Назад
                    </Button>
                    <span className="flex items-center px-4 text-sm text-muted-foreground">
                        Страница {currentPage} из {totalPages}
                    </span>
                    <Button
                        variant="outline"
                        disabled={currentPage >= totalPages}
                        onClick={() => fetchNews(currentPage + 1)}
                    >
                        Вперёд
                    </Button>
                </div>
            )}
        </div>
    )
}

