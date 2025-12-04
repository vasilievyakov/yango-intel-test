import { NextRequest, NextResponse } from 'next/server'

const API_URL = 'https://yango-intel-test.onrender.com'

export async function POST() {
    try {
        const response = await fetch(`${API_URL}/api/news/collect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        })
        
        const data = await response.json()
        return NextResponse.json(data)
    } catch (error) {
        console.error('API proxy error:', error)
        return NextResponse.json({ error: 'Collection failed' }, { status: 500 })
    }
}

