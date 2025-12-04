'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
    LayoutDashboard,
    DollarSign,
    Tag,
    Smartphone,
    MessageSquare,
    FileText,
    Database,
} from 'lucide-react'

const navigation = [
    { name: 'Обзор', href: '/', icon: LayoutDashboard },
    { name: 'Тарифы', href: '/tariffs', icon: DollarSign },
    { name: 'Промоакции', href: '/promos', icon: Tag },
    { name: 'Релизы', href: '/releases', icon: Smartphone },
    { name: 'Отзывы', href: '/reviews', icon: MessageSquare },
    { name: 'Дайджест', href: '/digest', icon: FileText },
    { name: 'Сбор данных', href: '/collection', icon: Database },
]

export function Sidebar() {
    const pathname = usePathname()

    return (
        <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
            <div className="flex grow flex-col gap-y-5 overflow-y-auto border-r border-border bg-card px-6 pb-4">
                <div className="flex h-16 shrink-0 items-center">
                    <h1 className="text-xl font-bold text-primary">
                        Yango Intel
                    </h1>
                </div>
                <nav className="flex flex-1 flex-col">
                    <ul role="list" className="flex flex-1 flex-col gap-y-1">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href
                            return (
                                <li key={item.name}>
                                    <Link
                                        href={item.href}
                                        className={cn(
                                            'group flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 transition-colors',
                                            isActive
                                                ? 'bg-primary text-primary-foreground'
                                                : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                                        )}
                                    >
                                        <item.icon
                                            className={cn(
                                                'h-5 w-5 shrink-0',
                                                isActive ? 'text-primary-foreground' : 'text-muted-foreground group-hover:text-accent-foreground'
                                            )}
                                        />
                                        {item.name}
                                    </Link>
                                </li>
                            )
                        })}
                    </ul>
                </nav>
            </div>
        </div>
    )
}
