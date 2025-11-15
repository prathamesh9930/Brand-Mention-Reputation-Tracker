// Global type definitions for the application

export interface Brand {
  id: number
  name: string
  keywords: string[]
  created_at: string
  is_active: boolean
  alert_threshold: number
  sentiment_threshold: number
}

export interface Mention {
  id: number
  brand_id: number
  content: string
  source: string
  source_url?: string
  author?: string
  created_at: string
  sentiment_score?: number
  sentiment_label?: string
  confidence?: number
  likes: number
  shares: number
  comments: number
}

export interface Alert {
  id: number
  brand_id: number
  alert_type: string
  title: string
  description?: string
  severity: string
  trigger_value?: number
  threshold_value?: number
  created_at: string
  is_read: boolean
  is_resolved: boolean
}

export interface SentimentAnalysis {
  brand_id: number
  brand_name: string
  time_range_hours: number
  total_mentions: number
  sentiment_breakdown: Record<string, any>
  sentiment_trend: Array<any>
  average_sentiment: number
}

export interface ApiResponse<T> {
  data: T
  status: string
  message?: string
}