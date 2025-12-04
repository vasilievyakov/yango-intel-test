import { NextResponse } from 'next/server'

// Clerk disabled temporarily - enable when you have API keys
// import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// const isPublicRoute = createRouteMatcher([
//     '/sign-in(.*)',
//     '/sign-up(.*)',
//     '/api/webhooks(.*)',
// ])

const hasClerkKeys = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && 
                     !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes('placeholder')

export default function middleware() {
    // If Clerk keys are configured, you can enable authentication
    // For now, allow all requests
    return NextResponse.next()
}

export const config = {
    matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
}
