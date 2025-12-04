import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

const isPublicRoute = createRouteMatcher([
    '/sign-in(.*)',
    '/sign-up(.*)',
    '/api/webhooks(.*)',
])

// Skip Clerk in development if keys are not set
const isDev = process.env.NODE_ENV === 'development'
const hasClerkKeys = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && 
                     !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes('placeholder')

export default isDev && !hasClerkKeys
    ? function middleware() {
          return NextResponse.next()
      }
    : clerkMiddleware((auth, request) => {
          if (!isPublicRoute(request)) {
              auth().protect()
          }
      })

export const config = {
    matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
}
