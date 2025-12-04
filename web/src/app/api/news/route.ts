import { NextRequest, NextResponse } from 'next/server'

const API_URL = 'https://yango-intel-test.onrender.com'

export async function GET(request: NextRequest) {
    const searchParams = request.nextUrl.searchParams
    const params = new URLSearchParams()
    
    searchParams.forEach((value, key) => {
        params.append(key, value)
    })
    
    try {
        const response = await fetch(`${API_URL}/api/news?${params}`, {
            headers: { 'Content-Type': 'application/json' },
        })
        
        const data = await response.json()
        return NextResponse.json(data)
    } catch (error) {
        console.error('API proxy error:', error)
        return NextResponse.json({ error: 'Failed to fetch news' }, { status: 500 })
    }
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json()
        
        const response = await fetch(`${API_URL}/api/news/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        })
        
        const data = await response.json()
        return NextResponse.json(data)
    } catch (error) {
        console.error('API proxy error:', error)
        return NextResponse.json({ error: 'Search failed' }, { status: 500 })
    }
}

