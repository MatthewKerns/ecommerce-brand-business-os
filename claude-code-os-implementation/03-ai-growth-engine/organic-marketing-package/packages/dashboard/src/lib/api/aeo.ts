/**
 * AEO (Answer Engine Optimization) API Client
 *
 * Provides typed functions for interacting with the AEO backend endpoints
 * including citation tracking, content optimization, and metrics.
 */

import { apiClient } from '@/lib/api-client'
import type { ApiClientOptions } from '@/lib/api-client'

// ============================================================================
// Types
// ============================================================================

export interface ContentMetadata {
  agent: string
  model: string
  tokens_used: number
  generation_time_ms: number
  timestamp: string
}

export interface CitationRecord {
  tracking_id: string
  platform: string
  query: string
  brand_mentioned: boolean
  citation_url: string | null
  citation_context: string | null
  opportunity_score: number
  query_category: string | null
  created_at: string | null
}

export interface PlatformStats {
  total_queries: number
  brand_mentioned: number
  citation_rate: number
  avg_opportunity_score?: number
  top_missed_queries?: string[]
}

export interface CitationStatusResponse {
  request_id: string
  summary: {
    total_tracked: number
    brand_mentioned: number
    citation_rate_percent: number
    avg_opportunity_score: number
    period_days: number
  }
  platforms: Record<string, PlatformStats>
  records: CitationRecord[]
  metadata: {
    generation_time_ms: number
    timestamp: string
  }
  status: string
}

export interface MissedOpportunity {
  query: string
  platform: string
  opportunity_score: number
  competitors_cited: Record<string, unknown> | null
  query_category: string | null
  date: string | null
}

export interface Recommendation {
  id: number
  type: string
  title: string
  description: string
  priority: string
  expected_impact: number | null
  effort: string | null
  ai_platform: string | null
}

export interface CitationAnalysisResponse {
  request_id: string
  brand: string
  analysis_period_days: number
  missed_opportunities: MissedOpportunity[]
  total_missed_opportunities: number
  recommendations: Recommendation[]
  platform_analysis: Record<string, PlatformStats>
  metadata: {
    generation_time_ms: number
    timestamp: string
  }
  status: string
}

export interface CompetitorStats {
  competitor: string
  total_queries: number
  times_mentioned: number
  citation_rate_percent: number
  platform_rates: Record<string, number>
}

export interface CompetitorCitationsResponse {
  request_id: string
  period_days: number
  brand_stats: {
    brand: string
    total_queries: number
    times_mentioned: number
    citation_rate_percent: number
  }
  competitors: CompetitorStats[]
  monitored_competitors: string[]
  metadata: {
    generation_time_ms: number
    timestamp: string
  }
  status: string
}

export interface ContentOptimizeResponse {
  request_id: string
  optimization_analysis: string
  optimization_level: string
  target_queries: string[]
  file_path: string
  metadata: ContentMetadata & { timestamp: string }
  status: string
}

export interface BlogGenerateResponse {
  request_id: string
  content: string
  file_path: string
  topic: string
  schemas: {
    faq?: Record<string, unknown>
    faq_error?: string
  }
  metadata: ContentMetadata & { timestamp: string }
  status: string
}

export interface DashboardOverview {
  citation_rate_percent: number
  citation_rate_change: number
  total_queries_tracked: number
  brand_mentions: number
  avg_opportunity_score: number
  pending_recommendations: number
  period_days: number
}

export interface OpportunityItem {
  query: string
  platform: string
  opportunity_score: number
  query_category: string | null
}

export interface CompetitorOverview {
  name: string
  citation_rate: number
  total_queries: number
}

export interface AEODashboardResponse {
  request_id: string
  overview: DashboardOverview
  platforms: Record<string, PlatformStats>
  categories: Record<string, {
    total: number
    mentioned: number
    citation_rate: number
  }>
  top_opportunities: OpportunityItem[]
  top_competitors: CompetitorOverview[]
  thresholds: {
    high_opportunity: number
    medium_opportunity: number
    alert_citation_drop: number
  }
  metadata: {
    generation_time_ms: number
    timestamp: string
  }
  status: string
}

export interface FAQContentResponse {
  request_id: string
  content: string
  file_path: string
  metadata: ContentMetadata
  status: string
}

export interface SchemaResponse {
  request_id: string
  schema: string
  schema_type: string
  metadata: ContentMetadata
  status: string
}

// ============================================================================
// Request Types
// ============================================================================

export interface CitationAnalyzeRequest {
  queries?: string[]
  platforms?: string[]
  brand_name?: string
}

export interface ContentOptimizeRequest {
  content: string
  target_queries?: string[]
  optimization_level?: 'light' | 'standard' | 'aggressive'
}

export interface BlogGenerateRequest {
  topic: string
  target_queries?: string[]
  word_count?: number
  include_faq_schema?: boolean
  include_product_schema?: boolean
}

export interface FAQGenerationRequest {
  topic: string
  num_questions?: number
  target_audience?: string
  include_product_mentions?: boolean
}

export interface FAQSchemaRequest {
  faq_items: Array<{ question: string; answer: string }>
}

export interface AIOptimizedContentRequest {
  question: string
  content_type?: 'guide' | 'article' | 'comparison' | 'tutorial'
  include_sources?: boolean
}

export interface ComparisonContentRequest {
  comparison_topic: string
  items_to_compare: string[]
  include_recommendation?: boolean
}

// ============================================================================
// API Base URL
// ============================================================================

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const AEO_BASE = `${API_BASE}/api/aeo`

// ============================================================================
// Citation Tracking Functions
// ============================================================================

/**
 * Get current citation tracking status across AI platforms.
 */
export async function getCitationStatus(params?: {
  platform?: string
  days?: number
  limit?: number
}, options?: ApiClientOptions): Promise<CitationStatusResponse> {
  const searchParams = new URLSearchParams()
  if (params?.platform) searchParams.set('platform', params.platform)
  if (params?.days) searchParams.set('days', params.days.toString())
  if (params?.limit) searchParams.set('limit', params.limit.toString())

  const query = searchParams.toString()
  const url = `${AEO_BASE}/citations/track${query ? `?${query}` : ''}`

  return apiClient.get<CitationStatusResponse>(url, {
    timeout: 15000,
    ...options,
  })
}

/**
 * Analyze citation opportunities across AI platforms.
 */
export async function analyzeCitations(
  request: CitationAnalyzeRequest,
  options?: ApiClientOptions
): Promise<CitationAnalysisResponse> {
  return apiClient.post<CitationAnalysisResponse>(
    `${AEO_BASE}/citations/analyze`,
    request,
    { timeout: 30000, ...options }
  )
}

/**
 * Get competitor citation comparison data.
 */
export async function getCompetitorCitations(params?: {
  days?: number
  competitor?: string
  platform?: string
}, options?: ApiClientOptions): Promise<CompetitorCitationsResponse> {
  const searchParams = new URLSearchParams()
  if (params?.days) searchParams.set('days', params.days.toString())
  if (params?.competitor) searchParams.set('competitor', params.competitor)
  if (params?.platform) searchParams.set('platform', params.platform)

  const query = searchParams.toString()
  const url = `${AEO_BASE}/citations/competitors${query ? `?${query}` : ''}`

  return apiClient.get<CompetitorCitationsResponse>(url, {
    timeout: 15000,
    ...options,
  })
}

// ============================================================================
// Content Optimization Functions
// ============================================================================

/**
 * Optimize content for better AI citation rates.
 */
export async function optimizeContent(
  request: ContentOptimizeRequest,
  options?: ApiClientOptions
): Promise<ContentOptimizeResponse> {
  return apiClient.post<ContentOptimizeResponse>(
    `${AEO_BASE}/content/optimize`,
    request,
    { timeout: 60000, ...options }
  )
}

/**
 * Generate a citation-optimized blog post.
 */
export async function generateCitationBlog(
  request: BlogGenerateRequest,
  options?: ApiClientOptions
): Promise<BlogGenerateResponse> {
  return apiClient.post<BlogGenerateResponse>(
    `${AEO_BASE}/blog/generate`,
    request,
    { timeout: 120000, ...options }
  )
}

// ============================================================================
// Content Generation Functions (existing AEO endpoints)
// ============================================================================

/**
 * Generate FAQ content optimized for AI citation.
 */
export async function generateFAQContent(
  request: FAQGenerationRequest,
  options?: ApiClientOptions
): Promise<FAQContentResponse> {
  return apiClient.post<FAQContentResponse>(
    `${AEO_BASE}/generate-faq`,
    request,
    { timeout: 60000, ...options }
  )
}

/**
 * Generate JSON-LD FAQ schema markup.
 */
export async function generateFAQSchema(
  request: FAQSchemaRequest,
  options?: ApiClientOptions
): Promise<SchemaResponse> {
  return apiClient.post<SchemaResponse>(
    `${AEO_BASE}/generate-faq-schema`,
    request,
    { timeout: 15000, ...options }
  )
}

/**
 * Generate JSON-LD Product schema markup.
 */
export async function generateProductSchema(
  productData: Record<string, unknown>,
  options?: ApiClientOptions
): Promise<SchemaResponse> {
  return apiClient.post<SchemaResponse>(
    `${AEO_BASE}/generate-product-schema`,
    { product_data: productData },
    { timeout: 15000, ...options }
  )
}

/**
 * Generate AI-optimized content for a specific question.
 */
export async function generateAIContent(
  request: AIOptimizedContentRequest,
  options?: ApiClientOptions
): Promise<FAQContentResponse> {
  return apiClient.post<FAQContentResponse>(
    `${AEO_BASE}/generate-ai-content`,
    request,
    { timeout: 60000, ...options }
  )
}

/**
 * Generate comparison content optimized for "best" and "vs" queries.
 */
export async function generateComparisonContent(
  request: ComparisonContentRequest,
  options?: ApiClientOptions
): Promise<FAQContentResponse> {
  return apiClient.post<FAQContentResponse>(
    `${AEO_BASE}/generate-comparison`,
    request,
    { timeout: 60000, ...options }
  )
}

// ============================================================================
// Metrics & Dashboard Functions
// ============================================================================

/**
 * Get comprehensive AEO dashboard metrics.
 */
export async function getAEODashboardMetrics(params?: {
  days?: number
}, options?: ApiClientOptions): Promise<AEODashboardResponse> {
  const searchParams = new URLSearchParams()
  if (params?.days) searchParams.set('days', params.days.toString())

  const query = searchParams.toString()
  const url = `${AEO_BASE}/metrics/dashboard${query ? `?${query}` : ''}`

  return apiClient.get<AEODashboardResponse>(url, {
    timeout: 15000,
    ...options,
  })
}

/**
 * Check AEO service health.
 */
export async function checkAEOHealth(
  options?: ApiClientOptions
): Promise<{ status: string; service: string; timestamp: string }> {
  return apiClient.get(`${AEO_BASE}/health`, {
    timeout: 5000,
    ...options,
  })
}

// ============================================================================
// Convenience exports
// ============================================================================

export const aeoApi = {
  // Citation tracking
  getCitationStatus,
  analyzeCitations,
  getCompetitorCitations,

  // Content optimization
  optimizeContent,
  generateCitationBlog,

  // Content generation
  generateFAQContent,
  generateFAQSchema,
  generateProductSchema,
  generateAIContent,
  generateComparisonContent,

  // Metrics
  getAEODashboardMetrics,
  checkAEOHealth,
}
