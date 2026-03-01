"use client";

import { TrendingUp, TrendingDown, Award, AlertCircle, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { ABTest, TestVariant } from "./ABTestManager";

/**
 * Variant performance metrics
 */
export interface VariantMetrics {
  /** Variant ID */
  variantId: string;
  /** Number of emails sent */
  sent: number;
  /** Number of emails opened */
  opens: number;
  /** Number of clicks */
  clicks: number;
  /** Number of conversions */
  conversions: number;
  /** Open rate percentage */
  openRate: number;
  /** Click rate percentage */
  clickRate: number;
  /** Conversion rate percentage */
  conversionRate: number;
}

/**
 * Statistical significance result
 */
export interface SignificanceResult {
  /** Is the result statistically significant? */
  isSignificant: boolean;
  /** Confidence level (e.g., 0.95 for 95%) */
  confidence: number;
  /** P-value */
  pValue: number;
  /** Improvement percentage */
  improvement: number;
  /** Winner variant ID (if significant) */
  winnerId?: string;
}

/**
 * ABTestResults Props
 */
export interface ABTestResultsProps {
  /** A/B test configuration */
  test: ABTest;
  /** Optional custom className */
  className?: string;
}

/**
 * Generate mock metrics for demonstration
 * In production, this would come from the analytics API
 */
function generateMockMetrics(test: ABTest): VariantMetrics[] {
  return test.variants.map((variant, index) => {
    // Simulate different performance for each variant
    const baseOpenRate = 0.25 + index * 0.05; // Variant A: 25%, B: 30%, etc.
    const baseClickRate = 0.08 + index * 0.02; // Variant A: 8%, B: 10%, etc.
    const baseConversionRate = 0.03 + index * 0.01; // Variant A: 3%, B: 4%, etc.

    const sent = test.status === "draft" ? 0 : Math.floor(Math.random() * 500) + 100;
    const opens = Math.floor(sent * baseOpenRate);
    const clicks = Math.floor(sent * baseClickRate);
    const conversions = Math.floor(sent * baseConversionRate);

    return {
      variantId: variant.id,
      sent,
      opens,
      clicks,
      conversions,
      openRate: sent > 0 ? (opens / sent) * 100 : 0,
      clickRate: sent > 0 ? (clicks / sent) * 100 : 0,
      conversionRate: sent > 0 ? (conversions / sent) * 100 : 0,
    };
  });
}

/**
 * Calculate statistical significance (simplified)
 * In production, use proper statistical testing (chi-square, z-test)
 */
function calculateSignificance(
  metrics: VariantMetrics[],
  primaryMetric: ABTest["primaryMetric"]
): SignificanceResult {
  if (metrics.length < 2) {
    return {
      isSignificant: false,
      confidence: 0,
      pValue: 1,
      improvement: 0,
    };
  }

  // Sort by primary metric (descending)
  const sorted = [...metrics].sort((a, b) => {
    const metricKey =
      primaryMetric === "open_rate"
        ? "openRate"
        : primaryMetric === "click_rate"
        ? "clickRate"
        : "conversionRate";
    return b[metricKey] - a[metricKey];
  });

  const winner = sorted[0];
  const control = sorted[1];

  // Get metric values
  const metricKey =
    primaryMetric === "open_rate"
      ? "openRate"
      : primaryMetric === "click_rate"
      ? "clickRate"
      : "conversionRate";

  const winnerRate = winner[metricKey];
  const controlRate = control[metricKey];

  // Calculate improvement percentage
  const improvement =
    controlRate > 0 ? ((winnerRate - controlRate) / controlRate) * 100 : 0;

  // Simplified significance calculation
  // In production, use proper statistical tests
  const sampleSize = Math.min(winner.sent, control.sent);
  const rateDifference = Math.abs(winnerRate - controlRate);

  // Mock p-value based on sample size and difference
  const pValue =
    sampleSize > 100 && rateDifference > 2
      ? 0.01
      : sampleSize > 50 && rateDifference > 5
      ? 0.05
      : 0.1;

  const confidence = 1 - pValue;
  const isSignificant = pValue < 0.05 && sampleSize >= 100;

  return {
    isSignificant,
    confidence,
    pValue,
    improvement,
    winnerId: isSignificant ? winner.variantId : undefined,
  };
}

/**
 * ABTestResults Component
 *
 * Display A/B test results with performance metrics and statistical analysis.
 *
 * Features:
 * - Performance metrics for each variant (sent, opens, clicks, conversions)
 * - Calculated rates (open rate, click rate, conversion rate)
 * - Statistical significance indicator
 * - Winner declaration (if significant)
 * - Visual comparison between variants
 * - Color-coded performance indicators
 * - Improvement percentage display
 *
 * @example
 * ```tsx
 * <ABTestResults test={abTest} />
 * ```
 */
export function ABTestResults({ test, className }: ABTestResultsProps) {
  // Generate metrics (in production, fetch from API)
  const metrics = generateMockMetrics(test);
  const significance = calculateSignificance(metrics, test.primaryMetric);

  // Get primary metric name
  const metricName =
    test.primaryMetric === "open_rate"
      ? "Open Rate"
      : test.primaryMetric === "click_rate"
      ? "Click Rate"
      : "Conversion Rate";

  // Get primary metric key
  const metricKey =
    test.primaryMetric === "open_rate"
      ? "openRate"
      : test.primaryMetric === "click_rate"
      ? "clickRate"
      : "conversionRate";

  // Find best performing variant
  const bestVariant = metrics.reduce((best, current) =>
    current[metricKey] > best[metricKey] ? current : best
  );

  return (
    <div className={cn("space-y-4", className)}>
      {/* Statistical Significance Banner */}
      {test.status !== "draft" && (
        <div
          className={cn(
            "rounded-lg border p-4",
            significance.isSignificant
              ? "border-green-200 bg-green-50"
              : "border-yellow-200 bg-yellow-50"
          )}
        >
          <div className="flex items-start gap-3">
            {significance.isSignificant ? (
              <CheckCircle2 className="h-5 w-5 flex-shrink-0 text-green-600" />
            ) : (
              <AlertCircle className="h-5 w-5 flex-shrink-0 text-yellow-600" />
            )}
            <div className="flex-1">
              <div
                className={cn(
                  "font-medium",
                  significance.isSignificant
                    ? "text-green-900"
                    : "text-yellow-900"
                )}
              >
                {significance.isSignificant
                  ? "Statistically Significant Result"
                  : "Not Yet Significant"}
              </div>
              <p
                className={cn(
                  "mt-1 text-sm",
                  significance.isSignificant
                    ? "text-green-800"
                    : "text-yellow-800"
                )}
              >
                {significance.isSignificant ? (
                  <>
                    Variant{" "}
                    {
                      test.variants.find((v) => v.id === significance.winnerId)
                        ?.label
                    }{" "}
                    is the clear winner with{" "}
                    <span className="font-medium">
                      {significance.improvement.toFixed(1)}% improvement
                    </span>{" "}
                    in {metricName.toLowerCase()} (
                    {(significance.confidence * 100).toFixed(0)}% confidence,
                    p={significance.pValue.toFixed(3)})
                  </>
                ) : (
                  <>
                    Continue testing to gather more data. Current confidence:{" "}
                    {(significance.confidence * 100).toFixed(0)}% (need 95%+
                    with p&lt;0.05)
                  </>
                )}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Variant Results Table */}
      <div className="overflow-hidden rounded-lg border border-slate-200">
        <table className="w-full">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-700">
                Variant
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wide text-slate-700">
                Sent
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wide text-slate-700">
                Opens
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wide text-slate-700">
                Clicks
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wide text-slate-700">
                Conversions
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wide text-slate-700">
                {metricName}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 bg-white">
            {test.variants.map((variant) => {
              const variantMetrics = metrics.find(
                (m) => m.variantId === variant.id
              );
              if (!variantMetrics) return null;

              const isWinner = significance.winnerId === variant.id;
              const isBest = bestVariant.variantId === variant.id;

              return (
                <tr
                  key={variant.id}
                  className={cn(
                    "transition-colors",
                    isWinner && "bg-green-50",
                    !isWinner && isBest && "bg-blue-50"
                  )}
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span
                        className={cn(
                          "flex h-6 w-6 items-center justify-center rounded text-xs font-bold",
                          isWinner
                            ? "bg-green-600 text-white"
                            : isBest
                            ? "bg-blue-600 text-white"
                            : "bg-slate-200 text-slate-700"
                        )}
                      >
                        {variant.label}
                      </span>
                      <div className="flex-1">
                        <div className="text-sm font-medium text-slate-900">
                          {variant.subject}
                        </div>
                        {isWinner && (
                          <div className="flex items-center gap-1 text-xs text-green-700">
                            <Award className="h-3 w-3" />
                            Winner
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right text-sm text-slate-700">
                    {variantMetrics.sent.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right text-sm text-slate-700">
                    {variantMetrics.opens.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right text-sm text-slate-700">
                    {variantMetrics.clicks.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right text-sm text-slate-700">
                    {variantMetrics.conversions.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <span
                        className={cn(
                          "text-sm font-semibold",
                          isWinner
                            ? "text-green-700"
                            : isBest
                            ? "text-blue-700"
                            : "text-slate-900"
                        )}
                      >
                        {variantMetrics[metricKey].toFixed(1)}%
                      </span>
                      {isBest &&
                        variantMetrics.variantId !== metrics[1]?.variantId && (
                          <TrendingUp className="h-4 w-4 text-green-600" />
                        )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Detailed Metrics Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {/* Open Rate Card */}
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <div className="text-sm font-medium text-slate-700">Open Rate</div>
          <div className="mt-2 space-y-2">
            {test.variants.map((variant) => {
              const variantMetrics = metrics.find(
                (m) => m.variantId === variant.id
              );
              if (!variantMetrics) return null;

              const maxOpenRate = Math.max(
                ...metrics.map((m) => m.openRate)
              );
              const isMax = variantMetrics.openRate === maxOpenRate;

              return (
                <div key={variant.id} className="flex items-center gap-2">
                  <span className="flex h-5 w-5 items-center justify-center rounded bg-slate-100 text-xs font-medium text-slate-700">
                    {variant.label}
                  </span>
                  <div className="flex-1">
                    <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                      <div
                        className={cn(
                          "h-full rounded-full transition-all",
                          isMax ? "bg-blue-600" : "bg-slate-300"
                        )}
                        style={{
                          width: `${Math.min(
                            (variantMetrics.openRate / 50) * 100,
                            100
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                  <span
                    className={cn(
                      "text-sm font-medium",
                      isMax ? "text-blue-700" : "text-slate-600"
                    )}
                  >
                    {variantMetrics.openRate.toFixed(1)}%
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Click Rate Card */}
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <div className="text-sm font-medium text-slate-700">Click Rate</div>
          <div className="mt-2 space-y-2">
            {test.variants.map((variant) => {
              const variantMetrics = metrics.find(
                (m) => m.variantId === variant.id
              );
              if (!variantMetrics) return null;

              const maxClickRate = Math.max(
                ...metrics.map((m) => m.clickRate)
              );
              const isMax = variantMetrics.clickRate === maxClickRate;

              return (
                <div key={variant.id} className="flex items-center gap-2">
                  <span className="flex h-5 w-5 items-center justify-center rounded bg-slate-100 text-xs font-medium text-slate-700">
                    {variant.label}
                  </span>
                  <div className="flex-1">
                    <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                      <div
                        className={cn(
                          "h-full rounded-full transition-all",
                          isMax ? "bg-blue-600" : "bg-slate-300"
                        )}
                        style={{
                          width: `${Math.min(
                            (variantMetrics.clickRate / 20) * 100,
                            100
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                  <span
                    className={cn(
                      "text-sm font-medium",
                      isMax ? "text-blue-700" : "text-slate-600"
                    )}
                  >
                    {variantMetrics.clickRate.toFixed(1)}%
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Conversion Rate Card */}
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <div className="text-sm font-medium text-slate-700">
            Conversion Rate
          </div>
          <div className="mt-2 space-y-2">
            {test.variants.map((variant) => {
              const variantMetrics = metrics.find(
                (m) => m.variantId === variant.id
              );
              if (!variantMetrics) return null;

              const maxConversionRate = Math.max(
                ...metrics.map((m) => m.conversionRate)
              );
              const isMax = variantMetrics.conversionRate === maxConversionRate;

              return (
                <div key={variant.id} className="flex items-center gap-2">
                  <span className="flex h-5 w-5 items-center justify-center rounded bg-slate-100 text-xs font-medium text-slate-700">
                    {variant.label}
                  </span>
                  <div className="flex-1">
                    <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                      <div
                        className={cn(
                          "h-full rounded-full transition-all",
                          isMax ? "bg-blue-600" : "bg-slate-300"
                        )}
                        style={{
                          width: `${Math.min(
                            (variantMetrics.conversionRate / 10) * 100,
                            100
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                  <span
                    className={cn(
                      "text-sm font-medium",
                      isMax ? "text-blue-700" : "text-slate-600"
                    )}
                  >
                    {variantMetrics.conversionRate.toFixed(1)}%
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Recommendations */}
      {test.status === "completed" && significance.isSignificant && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
          <div className="flex gap-3">
            <Award className="h-5 w-5 flex-shrink-0 text-blue-600" />
            <div className="text-sm text-blue-900">
              <p className="font-medium">Recommendation</p>
              <p className="mt-1 text-blue-800">
                Use Variant{" "}
                {
                  test.variants.find((v) => v.id === significance.winnerId)
                    ?.label
                }{" "}
                (&quot;
                {
                  test.variants.find((v) => v.id === significance.winnerId)
                    ?.subject
                }
                &quot;) for this sequence. It performed{" "}
                {significance.improvement.toFixed(1)}% better than other
                variants with statistical confidence.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Draft State */}
      {test.status === "draft" && (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-8 text-center">
          <AlertCircle className="mx-auto h-10 w-10 text-slate-400" />
          <p className="mt-3 text-sm text-slate-600">
            Start this test to begin collecting performance data
          </p>
        </div>
      )}
    </div>
  );
}
