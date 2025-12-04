import type {
    DashboardSummary,
    TariffComparison,
    PromoList,
    PromoFilters,
    ReleaseList,
    ReleaseFilters,
    ReviewList,
    ReviewFilters,
    ReviewStats,
    Digest,
    DigestList,
    CollectionStatus,
    CollectionLog,
} from './types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || ''

class ApiClient {
    private token: string | null = null

    setToken(token: string) {
        this.token = token
    }

    private async fetch<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${API_BASE}${endpoint}`

        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...(this.token && { Authorization: `Bearer ${this.token}` }),
                ...options.headers,
            },
        })

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
            throw new Error(error.detail || `API Error: ${response.status}`)
        }

        return response.json()
    }

    // Dashboard
    async getDashboardSummary(): Promise<DashboardSummary> {
        return this.fetch<DashboardSummary>('/api/dashboard/summary')
    }

    // Tariffs
    async getTariffComparison(type?: 'driver' | 'rider'): Promise<TariffComparison> {
        const params = type ? `?type=${type}` : ''
        return this.fetch<TariffComparison>(`/api/tariffs/comparison${params}`)
    }

    async getTariffHistory(competitorId: string, days = 30) {
        return this.fetch<{ history: Array<{ date: string; value: number }> }>(
            `/api/tariffs/history/${competitorId}?days=${days}`
        )
    }

    async getTariffChanges(days = 7) {
        return this.fetch<{
            changes: Array<{
                competitor: string
                field: string
                old_value: number
                new_value: number
                changed_at: string
            }>
        }>(`/api/tariffs/changes?days=${days}`)
    }

    // Promos
    async getPromos(filters?: PromoFilters): Promise<PromoList> {
        const params = new URLSearchParams()
        if (filters?.competitor_id) params.set('competitor_id', filters.competitor_id)
        if (filters?.active_only) params.set('active_only', 'true')
        if (filters?.target) params.set('target', filters.target)

        const query = params.toString() ? `?${params.toString()}` : ''
        return this.fetch<PromoList>(`/api/promos${query}`)
    }

    async getPromo(id: string) {
        return this.fetch<{ promo: import('./types').Promo }>(`/api/promos/${id}`)
    }

    // Releases
    async getReleases(filters?: ReleaseFilters): Promise<ReleaseList> {
        const params = new URLSearchParams()
        if (filters?.competitor_id) params.set('competitor_id', filters.competitor_id)
        if (filters?.platform) params.set('platform', filters.platform)
        if (filters?.category) params.set('category', filters.category)
        if (filters?.days) params.set('days', filters.days.toString())
        if (filters?.page) params.set('page', filters.page.toString())
        if (filters?.limit) params.set('limit', filters.limit.toString())

        const query = params.toString() ? `?${params.toString()}` : ''
        return this.fetch<ReleaseList>(`/api/releases${query}`)
    }

    async getReleaseTimeline(days = 30) {
        return this.fetch<{
            timeline: Array<{
                date: string
                releases: Array<{
                    competitor: string
                    platform: string
                    version: string
                }>
            }>
        }>(`/api/releases/timeline?days=${days}`)
    }

    // Reviews
    async getReviews(filters?: ReviewFilters): Promise<ReviewList> {
        const params = new URLSearchParams()
        if (filters?.competitor_id) params.set('competitor_id', filters.competitor_id)
        if (filters?.platform) params.set('platform', filters.platform)
        if (filters?.role) params.set('role', filters.role)
        if (filters?.sentiment) params.set('sentiment', filters.sentiment)
        if (filters?.category) params.set('category', filters.category)
        if (filters?.days) params.set('days', filters.days.toString())
        if (filters?.page) params.set('page', filters.page.toString())
        if (filters?.limit) params.set('limit', filters.limit.toString())

        const query = params.toString() ? `?${params.toString()}` : ''
        return this.fetch<ReviewList>(`/api/reviews${query}`)
    }

    async getReviewStats(competitorId?: string, days = 30): Promise<ReviewStats> {
        const params = new URLSearchParams()
        if (competitorId) params.set('competitor_id', competitorId)
        params.set('days', days.toString())

        return this.fetch<ReviewStats>(`/api/reviews/stats?${params.toString()}`)
    }

    async getReviewTrends(days = 7) {
        return this.fetch<{
            trends: Array<{
                competitor: string
                sentiment_change: number
                top_categories: string[]
            }>
        }>(`/api/reviews/trends?days=${days}`)
    }

    // Digest
    async generateDigest(period: 'week' | 'month', endDate: string): Promise<Digest> {
        return this.fetch<Digest>('/api/digest/generate', {
            method: 'POST',
            body: JSON.stringify({ period, end_date: endDate }),
        })
    }

    async getDigestHistory(): Promise<DigestList> {
        return this.fetch<DigestList>('/api/digest/history')
    }

    async getDigest(id: string): Promise<Digest> {
        return this.fetch<Digest>(`/api/digest/${id}`)
    }

    async exportDigest(id: string, format: 'pdf' | 'markdown'): Promise<Blob> {
        const response = await fetch(`${API_BASE}/api/digest/${id}/export`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(this.token && { Authorization: `Bearer ${this.token}` }),
            },
            body: JSON.stringify({ format }),
        })

        if (!response.ok) {
            throw new Error('Export failed')
        }

        return response.blob()
    }

    // Collection
    async getCollectionStatus(): Promise<CollectionStatus> {
        return this.fetch<CollectionStatus>('/api/collection/status')
    }

    async getCollectionLogs(filters?: { status?: string; days?: number }): Promise<{
        logs: CollectionLog[]
        total: number
    }> {
        const params = new URLSearchParams()
        if (filters?.status) params.set('status', filters.status)
        if (filters?.days) params.set('days', filters.days.toString())

        const query = params.toString() ? `?${params.toString()}` : ''
        return this.fetch(`/api/collection/logs${query}`)
    }

    // Competitors
    async getCompetitors(): Promise<{ competitors: import('./types').Competitor[] }> {
        return this.fetch('/api/competitors')
    }
}

export const api = new ApiClient()
