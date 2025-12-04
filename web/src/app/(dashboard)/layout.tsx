'use client'

import { useState } from 'react'
import { Sidebar } from '@/components/common/Sidebar'
import { Header } from '@/components/common/Header'
import { MobileSidebar } from '@/components/common/MobileSidebar'

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const [sidebarOpen, setSidebarOpen] = useState(false)

    return (
        <>
            <MobileSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
            <Sidebar />

            <div className="lg:pl-64">
                <Header onMenuClick={() => setSidebarOpen(true)} />

                <main className="py-6">
                    <div className="px-4 sm:px-6 lg:px-8">
                        {children}
                    </div>
                </main>
            </div>
        </>
    )
}
