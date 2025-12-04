'use client'

import { Apple, Smartphone } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

interface Release {
    id: string
    competitor: string
    platform: 'ios' | 'android'
    version: string
    releaseDate: string
    releaseNotes?: string
    categories?: string[]
    significance?: 'major' | 'minor' | 'bugfix'
}

interface ReleaseTimelineProps {
    releases: Release[]
    className?: string
}

const categoryLabels: Record<string, string> = {
    pricing: 'Тарифы',
    ux_ui: 'UX/UI',
    safety: 'Безопасность',
    driver_exp: 'Водители',
    rider_exp: 'Пассажиры',
    promo: 'Промо',
    other: 'Другое',
}

const significanceColors: Record<string, string> = {
    major: 'bg-blue-500',
    minor: 'bg-green-500',
    bugfix: 'bg-gray-400',
}

export function ReleaseTimeline({ releases, className }: ReleaseTimelineProps) {
    if (releases.length === 0) {
        return (
            <div className="text-center py-12">
                <p className="text-muted-foreground">Нет релизов по выбранным фильтрам</p>
            </div>
        )
    }

    return (
        <div className={cn('relative', className)}>
            {/* Timeline line */}
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />

            <div className="space-y-6">
                {releases.map((release) => (
                    <div key={release.id} className="relative pl-10">
                        {/* Timeline dot */}
                        <div
                            className={cn(
                                'absolute left-2.5 top-1 h-3 w-3 rounded-full border-2 border-background',
                                significanceColors[release.significance || 'minor']
                            )}
                        />

                        <div className="rounded-lg border bg-card p-4 shadow-sm">
                            <div className="flex items-start justify-between">
                                <div className="flex items-center gap-2">
                                    {release.platform === 'ios' ? (
                                        <Apple className="h-5 w-5 text-muted-foreground" />
                                    ) : (
                                        <Smartphone className="h-5 w-5 text-muted-foreground" />
                                    )}
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <span className="font-semibold">{release.competitor}</span>
                                            <Badge variant="outline" className="text-xs">
                                                v{release.version}
                                            </Badge>
                                        </div>
                                        <p className="text-sm text-muted-foreground">
                                            {format(new Date(release.releaseDate), 'd MMMM yyyy', { locale: ru })}
                                        </p>
                                    </div>
                                </div>
                                <Badge
                                    variant={release.platform === 'ios' ? 'default' : 'secondary'}
                                    className="text-xs"
                                >
                                    {release.platform === 'ios' ? 'iOS' : 'Android'}
                                </Badge>
                            </div>

                            {release.releaseNotes && (
                                <p className="mt-3 text-sm text-muted-foreground line-clamp-2">
                                    {release.releaseNotes}
                                </p>
                            )}

                            {release.categories && release.categories.length > 0 && (
                                <div className="mt-3 flex flex-wrap gap-1">
                                    {release.categories.map((cat) => (
                                        <Badge key={cat} variant="outline" className="text-xs">
                                            {categoryLabels[cat] || cat}
                                        </Badge>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
