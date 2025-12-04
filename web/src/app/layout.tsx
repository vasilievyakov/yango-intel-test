import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ClerkProvider } from '@clerk/nextjs'
import './globals.css'

const inter = Inter({ subsets: ['latin', 'cyrillic'] })

export const metadata: Metadata = {
    title: 'Yango Competitive Intelligence',
    description: 'Мониторинг конкурентов на рынке ride-hailing в Перу',
}

// Check if Clerk is properly configured
const hasClerkKeys = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && 
                     !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes('placeholder')

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const content = (
        <html lang="ru">
            <body className={inter.className}>{children}</body>
        </html>
    )

    // Skip ClerkProvider in development if keys are not set
    if (!hasClerkKeys) {
        return content
    }

    return <ClerkProvider>{content}</ClerkProvider>
}
