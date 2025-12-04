'use client'

import { UserButton, useAuth } from '@clerk/nextjs'
import { Menu, User } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface HeaderProps {
    onMenuClick?: () => void
}

// Check if Clerk is configured
const hasClerkKeys = typeof window !== 'undefined' && 
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && 
    !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes('placeholder')

function UserSection() {
    // Only use Clerk if it's properly configured
    if (!hasClerkKeys) {
        return (
            <div className="flex items-center justify-center h-8 w-8 rounded-full bg-primary text-primary-foreground">
                <User className="h-4 w-4" />
            </div>
        )
    }

    return (
        <UserButton
            afterSignOutUrl="/sign-in"
            appearance={{
                elements: {
                    avatarBox: "h-8 w-8"
                }
            }}
        />
    )
}

export function Header({ onMenuClick }: HeaderProps) {
    return (
        <header className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-border bg-background px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
            <Button
                variant="ghost"
                size="icon"
                className="lg:hidden"
                onClick={onMenuClick}
            >
                <Menu className="h-6 w-6" />
                <span className="sr-only">Открыть меню</span>
            </Button>

            <div className="h-6 w-px bg-border lg:hidden" />

            <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
                <div className="flex flex-1 items-center">
                    <h2 className="text-lg font-semibold text-foreground lg:hidden">
                        Yango Intel
                    </h2>
                </div>
                <div className="flex items-center gap-x-4 lg:gap-x-6">
                    <UserSection />
                </div>
            </div>
        </header>
    )
}
