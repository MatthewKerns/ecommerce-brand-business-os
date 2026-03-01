/**
 * Analytics Module - Email tracking and performance measurement
 *
 * Exports:
 * - HMAC signing utilities for secure tracking
 * - Tracking pixel generation for email opens
 * - Click URL wrapping for link tracking
 * - Token parsing and verification
 * - Email event data models
 * - Analytics storage and metrics
 * - A/B testing system with variant management
 * - Statistical significance testing and analysis
 */

// HMAC Utilities
export {
  HmacService,
  getHmacService,
  resetHmacService,
  type SignedData,
  type VerificationResult,
  type HmacConfig,
} from './hmac';

// Tracking System
export {
  TrackingService,
  getTrackingService,
  resetTrackingService,
  generateTrackingPixel,
  generateClickTrackingUrl,
  parseTrackingToken,
  type TrackingPixelParams,
  type ClickTrackingParams,
  type TrackingConfig,
  type ParsedTrackingData,
} from './tracking';

// Data Models
export {
  type EmailEvent,
  type EmailEventType,
  type ConversionType,
  type BounceType,
  type EmailEventData,
  type ClickEventData,
  type ConversionEventData,
  type BounceEventData,
  type OpenEventData,
  type EmailEventCreateInput,
  type ClickEventInput,
  type ConversionEventInput,
  type OpenEventInput,
  type EmailEventFilter,
  type EmailEventSort,
  type EmailEventPagination,
  type EmailEventListResponse,
  type EmailMetrics,
  type SequenceMetrics,
  type StepMetrics,
  type CampaignMetrics,
  type VariantMetrics,
  type TimeInterval,
  type TimeSeriesDataPoint,
  type TimeSeriesMetrics,
  type FunnelStep,
  type EmailFunnel,
  type CohortMetrics,
  type EmailEventCount,
  type TopLink,
  type DeviceBreakdown,
  type LocationBreakdown,
} from './models';

// Storage
export {
  type IAnalyticsStorage,
  type AnalyticsStorageConfig,
  MemoryAnalyticsStorage,
  GoogleSheetsAnalyticsStorage,
  createAnalyticsStorage,
  getAnalyticsStorage,
  resetAnalyticsStorage,
} from './storage';

// Metrics Aggregation Engine
export {
  MetricsAggregationEngine,
  getMetricsEngine,
  resetMetricsEngine,
  type PerformanceReportOptions,
  type PerformanceReport,
  type ComparisonReport,
  type SequencePerformanceReport,
} from './metrics';

// A/B Testing System
export {
  ABTestManager,
  getABTestManager,
  resetABTestManager,
  type ABTest,
  type ABVariant,
  type ABTestStatus,
  type ABTestType,
  type ABTestAssignment,
  type ABTestFilter,
  type ABTestResults,
} from './ab-testing';

// Statistical Analysis
export {
  calculateSignificance,
  calculateChiSquare,
  calculateZScore,
  calculatePValue,
  calculateConfidenceInterval,
  calculateCohenH,
  calculatePower,
  calculateMinimumSampleSize,
  calculateSampleSizeRequirements,
  compareVariantsToControl,
  determineWinner,
  calculateBayesianCredibleInterval,
  type SignificanceTestResult,
  type ConfidenceInterval,
  type ProportionTestResult,
  type SampleSizeRequirement,
} from './statistics';
