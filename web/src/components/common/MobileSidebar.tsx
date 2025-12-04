'use client'

import { Fragment } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
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

interface MobileSidebarProps {
    open: boolean
    onClose: () => void
}

export function MobileSidebar({ open, onClose }: MobileSidebarProps) {
    const pathname = usePathname()

    if (!open) return null

    return (
        <div className="relative z-50 lg:hidden">
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-gray-900/80 transition-opacity"
                onClick={onClose}
            />

            {/* Sidebar panel */}
            <div className="fixed inset-0 flex">
                <div className="relative mr-16 flex w-full max-w-xs flex-1">
                    {/* Close button */}
                    <div className="absolute left-full top-0 flex w-16 justify-center pt-5">
                        <Button variant="ghost" size="icon" onClick={onClose}>
                            <X className="h-6 w-6 text-white" />
                            <span className="sr-only">Закрыть меню</span>
                        </Button>
                    </div>

                    {/* Sidebar content */}
                    <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-card px-6 pb-4">
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
                                                onClick={onClose}
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
            </div>
        </div>
    )
}
