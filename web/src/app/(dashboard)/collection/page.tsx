'use client'

import { useState } from 'react'
import { formatDistanceToNow, format } from 'date-fns'
import { ru } from 'date-fns/locale'
import {
    Database,
    CheckCircle2,
    AlertCircle,
    XCircle,
    Clock,
    RefreshCw,
    ExternalLink,
    Globe,
    Apple,
    Smartphone,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

// Mock data for collection sources
const mockSources = [
    {
        task_name: 'indriver-driver-pe',
        competitor: 'InDriver',
        source_type: 'website',
        last_success: '2025-01-15T10:30:00Z',
        last_status: 'success' as const,
        items_collected: 12,
        url: 'https://indriver.com/pe/driver',
    },
    {
        task_name: 'uber-driver-pe',
        competitor: 'Uber',
        source_type: 'website',
        last_success: '2025-01-15T10:25:00Z',
        last_status: 'success' as const,
        items_collected: 8,
        url: 'https://uber.com/pe/es/drive',
    },
    {
        task_name: 'didi-driver-pe',
        competitor: 'Didi',
        source_type: 'website',
        last_success: '2025-01-15T09:00:00Z',
        last_status: 'warning' as const,
        items_collected: 5,
        url: 'https://web.didiglobal.com/pe/driver',
    },
    {
        task_name: 'cabify-driver-pe',
        competitor: 'Cabify',
        source_type: 'website',
        last_success: '2025-01-14T18:00:00Z',
        last_status: 'failed' as const,
        items_collected: 0,
        url: 'https://cabify.com/pe/driver',
    },
    {
        task_name: 'appstore-indriver',
        competitor: 'InDriver',
        source_type: 'appstore',
        last_success: '2025-01-15T08:00:00Z',
        last_status: 'success' as const,
        items_collected: 45,
        url: 'https://apps.apple.com/pe/app/id1018263498',
    },
    {
        task_name: 'appstore-uber',
        competitor: 'Uber',
        source_type: 'appstore',
        last_success: '2025-01-15T08:00:00Z',
        last_status: 'success' as const,
        items_collected: 38,
        url: 'https://apps.apple.com/pe/app/id368677368',
    },
    {
        task_name: 'playstore-indriver',
        competitor: 'InDriver',
        source_type: 'playstore',
        last_success: '2025-01-15T08:15:00Z',
        last_status: 'success' as const,
        items_collected: 62,
        url: 'https://play.google.com/store/apps/details?id=sinet.startup.inDriver',
    },
    {
        task_name: 'playstore-uber',
        competitor: 'Uber',
        source_type: 'playstore',
        last_success: '2025-01-15T08:15:00Z',
        last_status: 'success' as const,
        items_collected: 55,
        url: 'https://play.google.com/store/apps/details?id=com.ubercab',
    },
]

const mockLogs = [
    {
        id: '1',
        task_name: 'cabify-driver-pe',
        competitor: 'Cabify',
        source_type: 'website',
        status: 'failed' as const,
        error_message: 'Connection timeout: сервер не ответил за 30 секунд',
        items_collected: 0,
        completed_at: '2025-01-15T12:30:00Z',
    },
    {
        id: '2',
        task_name: 'indriver-driver-pe',
        competitor: 'InDriver',
        source_type: 'website',
        status: 'success' as const,
        items_collected: 12,
        completed_at: '2025-01-15T10:30:00Z',
    },
    {
        id: '3',
        task_name: 'uber-driver-pe',
        competitor: 'Uber',
        source_type: 'website',
        status: 'success' as const,
        items_collected: 8,
        completed_at: '2025-01-15T10:25:00Z',
    },
    {
        id: '4',
        task_name: 'didi-driver-pe',
        competitor: 'Didi',
        source_type: 'website',
        status: 'partial' as const,
        error_message: 'Не удалось получить данные о бонусах',
        items_collected: 5,
        completed_at: '2025-01-15T09:00:00Z',
    },
    {
        id: '5',
        task_name: 'playstore-indriver',
        competitor: 'InDriver',
        source_type: 'playstore',
        status: 'success' as const,
        items_collected: 62,
        completed_at: '2025-01-15T08:15:00Z',
    },
]

const statusConfig = {
    success: {
        icon: CheckCircle2,
        label: 'Успешно',
        color: 'text-green-600',
        bgColor: 'bg-green-100',
        badgeVariant: 'default' as const,
    },
    warning: {
        icon: AlertCircle,
        label: 'Частично',
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-100',
        badgeVariant: 'secondary' as const,
    },
    partial: {
        icon: AlertCircle,
        label: 'Частично',
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-100',
        badgeVariant: 'secondary' as const,
    },
    failed: {
        icon: XCircle,
        label: 'Ошибка',
        color: 'text-red-600',
        bgColor: 'bg-red-100',
        badgeVariant: 'destructive' as const,
    },
    never: {
        icon: Clock,
        label: 'Не запускался',
        color: 'text-gray-500',
        bgColor: 'bg-gray-100',
        badgeVariant: 'outline' as const,
    },
}

const sourceTypeConfig = {
    website: { icon: Globe, label: 'Сайт' },
    appstore: { icon: Apple, label: 'App Store' },
    playstore: { icon: Smartphone, label: 'Play Store' },
}

export default function CollectionPage() {
    const [statusFilter, setStatusFilter] = useState('all')
    const [isRefreshing, setIsRefreshing] = useState(false)

    const filteredSources =
        statusFilter === 'all'
            ? mockSources
            : mockSources.filter((s) => s.last_status === statusFilter)

    const successCount = mockSources.filter((s) => s.last_status === 'success').length
    const warningCount = mockSources.filter((s) => s.last_status === 'warning').length
    const failedCount = mockSources.filter((s) => s.last_status === 'failed').length

    const handleRefresh = async () => {
        setIsRefreshing(true)
        await new Promise((resolve) => setTimeout(resolve, 1500))
        setIsRefreshing(false)
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Сбор данных</h1>
                    <p className="text-muted-foreground">
                        Статус парсинга и логи последних операций
                    </p>
                </div>
                <Button onClick={handleRefresh} disabled={isRefreshing}>
                    <RefreshCw
                        className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`}
                    />
                    Обновить
                </Button>
            </div>

            {/* Summary Cards */}
            <div className="grid gap-4 md:grid-cols-4">
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-muted">
                                <Database className="h-5 w-5 text-muted-foreground" />
                            </div>
                            <div>
                                <div className="text-2xl font-bold">{mockSources.length}</div>
                                <p className="text-sm text-muted-foreground">Источников</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-green-100">
                                <CheckCircle2 className="h-5 w-5 text-green-600" />
                            </div>
                            <div>
                                <div className="text-2xl font-bold">{successCount}</div>
                                <p className="text-sm text-muted-foreground">Работают</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-yellow-100">
                                <AlertCircle className="h-5 w-5 text-yellow-600" />
                            </div>
                            <div>
                                <div className="text-2xl font-bold">{warningCount}</div>
                                <p className="text-sm text-muted-foreground">С проблемами</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-red-100">
                                <XCircle className="h-5 w-5 text-red-600" />
                            </div>
                            <div>
                                <div className="text-2xl font-bold">{failedCount}</div>
                                <p className="text-sm text-muted-foreground">Ошибки</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Tabs defaultValue="sources" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="sources">Источники</TabsTrigger>
                    <TabsTrigger value="logs">Логи</TabsTrigger>
                </TabsList>

                <TabsContent value="sources" className="space-y-4">
                    <div className="flex items-center gap-4">
                        <Select value={statusFilter} onValueChange={setStatusFilter}>
                            <SelectTrigger className="w-[180px]">
                                <SelectValue placeholder="Статус" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Все статусы</SelectItem>
                                <SelectItem value="success">Успешно</SelectItem>
                                <SelectItem value="warning">Частично</SelectItem>
                                <SelectItem value="failed">Ошибки</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    <Card>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Источник</TableHead>
                                    <TableHead>Конкурент</TableHead>
                                    <TableHead>Тип</TableHead>
                                    <TableHead>Статус</TableHead>
                                    <TableHead>Последний сбор</TableHead>
                                    <TableHead className="text-right">Элементов</TableHead>
                                    <TableHead></TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {filteredSources.map((source) => {
                                    const status = statusConfig[source.last_status]
                                    const sourceType = sourceTypeConfig[source.source_type as keyof typeof sourceTypeConfig]
                                    const StatusIcon = status.icon
                                    const SourceIcon = sourceType.icon

                                    return (
                                        <TableRow key={source.task_name}>
                                            <TableCell className="font-medium">
                                                {source.task_name}
                                            </TableCell>
                                            <TableCell>{source.competitor}</TableCell>
                                            <TableCell>
                                                <div className="flex items-center gap-2">
                                                    <SourceIcon className="h-4 w-4 text-muted-foreground" />
                                                    <span className="text-sm">
                                                        {sourceType.label}
                                                    </span>
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <div className="flex items-center gap-2">
                                                    <StatusIcon
                                                        className={`h-4 w-4 ${status.color}`}
                                                    />
                                                    <span className={`text-sm ${status.color}`}>
                                                        {status.label}
                                                    </span>
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                {source.last_success ? (
                                                    <span className="text-sm text-muted-foreground">
                                                        {formatDistanceToNow(
                                                            new Date(source.last_success),
                                                            { addSuffix: true, locale: ru }
                                                        )}
                                                    </span>
                                                ) : (
                                                    <span className="text-sm text-muted-foreground">
                                                        —
                                                    </span>
                                                )}
                                            </TableCell>
                                            <TableCell className="text-right">
                                                {source.items_collected}
                                            </TableCell>
                                            <TableCell>
                                                <a
                                                    href={source.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-muted-foreground hover:text-foreground"
                                                >
                                                    <ExternalLink className="h-4 w-4" />
                                                </a>
                                            </TableCell>
                                        </TableRow>
                                    )
                                })}
                            </TableBody>
                        </Table>
                    </Card>
                </TabsContent>

                <TabsContent value="logs" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Последние операции</CardTitle>
                            <CardDescription>
                                Детальная информация о сборе данных
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {mockLogs.map((log) => {
                                const status = statusConfig[log.status]
                                const StatusIcon = status.icon
                                const sourceType = sourceTypeConfig[log.source_type as keyof typeof sourceTypeConfig]

                                return (
                                    <div
                                        key={log.id}
                                        className={`p-4 rounded-lg border ${
                                            log.status === 'failed'
                                                ? 'border-red-200 bg-red-50/50'
                                                : log.status === 'partial'
                                                ? 'border-yellow-200 bg-yellow-50/50'
                                                : 'border-border'
                                        }`}
                                    >
                                        <div className="flex items-start justify-between">
                                            <div className="flex items-start gap-3">
                                                <div
                                                    className={`p-2 rounded-lg ${status.bgColor}`}
                                                >
                                                    <StatusIcon
                                                        className={`h-4 w-4 ${status.color}`}
                                                    />
                                                </div>
                                                <div>
                                                    <div className="flex items-center gap-2">
                                                        <span className="font-medium">
                                                            {log.task_name}
                                                        </span>
                                                        <Badge variant="outline" className="text-xs">
                                                            {log.competitor}
                                                        </Badge>
                                                    </div>
                                                    {log.error_message && (
                                                        <p className="text-sm text-red-600 mt-1">
                                                            {log.error_message}
                                                        </p>
                                                    )}
                                                    <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                                                        <span className="flex items-center gap-1">
                                                            <sourceType.icon className="h-3 w-3" />
                                                            {sourceType.label}
                                                        </span>
                                                        <span>
                                                            {log.items_collected} элементов
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="text-sm text-muted-foreground">
                                                {format(new Date(log.completed_at), 'HH:mm', {
                                                    locale: ru,
                                                })}
                                            </div>
                                        </div>
                                    </div>
                                )
                            })}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}

