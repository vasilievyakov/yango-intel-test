// Competitor
export interface Competitor {
    id: string
    name: string
    slug: string
    country: string
    logo_url?: string
    website_driver?: string
    website_rider?: string
    appstore_id?: string
    playstore_id?: string
    is_active: boolean
}

// Driver Tariff
export interface DriverTariff {
    id: string
    competitor: Competitor
    commission_rate: number
    min_fare?: number
    signup_bonus?: number
    referral_bonus?: number
    requirements?: string[]
    benefits?: string[]
    currency: string
    collected_at: string
    is_latest: boolean
}

// Rider Tariff
export interface RiderTariff {
    id: string
    competitor: Competitor
    service_type: string
    base_fare?: number
    per_km_rate?: number
    per_min_rate?: number
    booking_fee?: number
    currency: string
    collected_at: string
    is_latest: boolean
}

// Tariff Comparison
export interface TariffComparison {
    comparison: Array<{
        competitor: string
        competitor_id: string
        logo_url?: string
        driver?: {
            commission_rate: number
            signup_bonus?: number
            referral_bonus?: number
        }
        rider?: {
            base_fare?: number
            per_km_rate?: number
            per_min_rate?: number
        }
    }>
    updated_at: string
}

// Promo
export interface Promo {
    id: string
    competitor: Competitor
    title: string
    description?: string
    code?: string
    discount_type: 'percent' | 'fixed' | 'free_ride'
    discount_value?: number
    valid_from?: string
    valid_until?: string
    conditions?: string
    target_audience: 'driver' | 'rider' | 'unknown'
    is_active: boolean
    collected_at: string
}

export interface PromoFilters {
    competitor_id?: string
    active_only?: boolean
    target?: 'driver' | 'rider'
}

export interface PromoList {
    promos: Promo[]
    total: number
}

// Release
export interface Release {
    id: string
    competitor: Competitor
    platform: 'ios' | 'android'
    version: string
    release_date?: string
    release_notes?: string
    rating?: number
    rating_count?: number
    categories?: string[]
    significance?: 'major' | 'minor' | 'bugfix'
    collected_at: string
}

export interface ReleaseFilters {
    competitor_id?: string
    platform?: 'ios' | 'android'
    category?: string
    days?: number
    page?: number
    limit?: number
}

export interface ReleaseList {
    releases: Release[]
    total: number
    page: number
    pages: number
}

// Review
export interface Review {
    id: string
    external_id: string
    competitor: Competitor
    platform: 'ios' | 'android'
    author?: string
    rating: number
    text?: string
    review_date?: string
    app_version?: string
    language: string
    role: 'driver' | 'rider' | 'unknown'
    sentiment: 'positive' | 'neutral' | 'negative'
    categories?: string[]
    collected_at: string
}

export interface ReviewFilters {
    competitor_id?: string
    platform?: 'ios' | 'android'
    role?: 'driver' | 'rider'
    sentiment?: 'positive' | 'neutral' | 'negative'
    category?: string
    days?: number
    page?: number
    limit?: number
}

export interface ReviewList {
    reviews: Review[]
    total: number
    page: number
    pages: number
}

export interface ReviewStats {
    total: number
    by_sentiment: {
        positive: number
        neutral: number
        negative: number
    }
    by_competitor: Array<{
        competitor: string
        competitor_id: string
        total: number
        positive: number
        neutral: number
        negative: number
        avg_rating: number
    }>
    trending_categories: Array<{
        category: string
        count: number
        change: number
    }>
}

// Digest
export interface Digest {
    id: string
    period_start: string
    period_end: string
    content: string
    metadata?: {
        releases_count: number
        tariff_changes_count: number
        active_promos_count: number
        model: string
    }
    created_by?: string
    created_at: string
}

export interface DigestList {
    digests: Digest[]
    total: number
}

// Collection Status
export interface CollectionLog {
    id: string
    source_type: 'website' | 'appstore' | 'playstore'
    competitor?: Competitor
    task_name: string
    url?: string
    status: 'success' | 'partial' | 'failed'
    error_message?: string
    items_collected: number
    started_at?: string
    completed_at: string
}

export interface CollectionStatus {
    sources: Array<{
        task_name: string
        competitor: string
        source_type: string
        last_success?: string
        last_status: 'success' | 'partial' | 'failed' | 'never'
        items_collected: number
    }>
    last_update: string
    health: 'healthy' | 'warning' | 'error'
}

// Dashboard Summary
export interface DashboardSummary {
    last_collection?: string
    new_releases_week: number
    new_reviews_week: number
    active_promos: Record<string, number>
    health_status: 'healthy' | 'warning' | 'error'
    tariff_changes_week: number
}

// API Responses
export interface ApiError {
    detail: string
    status_code: number
}
