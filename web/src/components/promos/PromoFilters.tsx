'use client'

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'

interface PromoFiltersProps {
    competitors: { id: string; name: string }[]
    selectedCompetitor: string
    onCompetitorChange: (value: string) => void
    activeOnly: boolean
    onActiveOnlyChange: (value: boolean) => void
    targetAudience: string
    onTargetAudienceChange: (value: string) => void
}

export function PromoFilters({
    competitors,
    selectedCompetitor,
    onCompetitorChange,
    activeOnly,
    onActiveOnlyChange,
    targetAudience,
    onTargetAudienceChange,
}: PromoFiltersProps) {
    return (
        <div className="flex flex-wrap gap-4">
            <Select value={selectedCompetitor} onValueChange={onCompetitorChange}>
                <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Конкурент" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="all">Все конкуренты</SelectItem>
                    {competitors.map((c) => (
                        <SelectItem key={c.id} value={c.id}>
                            {c.name}
                        </SelectItem>
                    ))}
                </SelectContent>
            </Select>

            <Select
                value={activeOnly ? 'active' : 'all'}
                onValueChange={(v) => onActiveOnlyChange(v === 'active')}
            >
                <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="Статус" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="all">Все промо</SelectItem>
                    <SelectItem value="active">Активные</SelectItem>
                </SelectContent>
            </Select>

            <Select value={targetAudience} onValueChange={onTargetAudienceChange}>
                <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="Аудитория" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="all">Все</SelectItem>
                    <SelectItem value="driver">Водители</SelectItem>
                    <SelectItem value="rider">Пассажиры</SelectItem>
                </SelectContent>
            </Select>
        </div>
    )
}
