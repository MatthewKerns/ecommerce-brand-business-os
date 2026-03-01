/**
 * Statistical Analysis - Calculate significance for A/B test results
 *
 * Features:
 * - Chi-square test for categorical data
 * - Z-test for proportions
 * - P-value calculation
 * - Confidence intervals
 * - Statistical power analysis
 * - Minimum sample size calculation
 * - Effect size (Cohen's h) for proportion differences
 */

// ============================================================
// Types
// ============================================================

export interface SignificanceTestResult {
  // Test statistics
  chiSquare: number;
  zScore: number;
  pValue: number;
  degreesOfFreedom: number;

  // Significance indicators
  isSignificant: boolean;
  confidenceLevel: number; // 90, 95, or 99

  // Proportions and differences
  controlRate: number;
  variantRate: number;
  absoluteDifference: number;
  relativeDifference: number; // percentage change

  // Effect size
  effectSize: number; // Cohen's h
  effectSizeInterpretation: 'negligible' | 'small' | 'medium' | 'large';

  // Sample information
  controlSampleSize: number;
  variantSampleSize: number;
  totalSampleSize: number;

  // Statistical power
  statisticalPower?: number;

  // Recommendations
  recommendation: 'continue' | 'declare_winner' | 'stop_test' | 'insufficient_data';
  minimumSampleSizeReached: boolean;
}

export interface ConfidenceInterval {
  lower: number;
  upper: number;
  confidenceLevel: number;
}

export interface ProportionTestResult {
  proportion1: number;
  proportion2: number;
  difference: number;
  standardError: number;
  zScore: number;
  pValue: number;
  confidenceInterval: ConfidenceInterval;
}

export interface SampleSizeRequirement {
  minimumPerVariant: number;
  minimumTotal: number;
  detectedEffectSize: number;
  power: number;
  alpha: number; // significance level
}

// ============================================================
// Main Statistical Tests
// ============================================================

/**
 * Calculate statistical significance for A/B test comparing two proportions
 *
 * @param controlTotal - Total sample size for control group
 * @param controlConversions - Number of conversions in control group
 * @param variantTotal - Total sample size for variant group
 * @param variantConversions - Number of conversions in variant group
 * @param confidenceLevel - Desired confidence level (90, 95, or 99)
 * @returns Comprehensive significance test results
 */
export function calculateSignificance(
  controlTotal: number,
  controlConversions: number,
  variantTotal: number,
  variantConversions: number,
  confidenceLevel: 90 | 95 | 99 = 95
): SignificanceTestResult {
  // Validate inputs
  validateInputs(controlTotal, controlConversions, variantTotal, variantConversions);

  // Calculate conversion rates
  const controlRate = controlConversions / controlTotal;
  const variantRate = variantConversions / variantTotal;

  // Calculate differences
  const absoluteDifference = variantRate - controlRate;
  const relativeDifference = controlRate > 0 ? (absoluteDifference / controlRate) * 100 : 0;

  // Chi-square test
  const chiSquare = calculateChiSquare(
    controlTotal,
    controlConversions,
    variantTotal,
    variantConversions
  );

  // Z-test for proportions
  const zScore = calculateZScore(
    controlRate,
    variantRate,
    controlTotal,
    variantTotal
  );

  // P-value from z-score (two-tailed test)
  const pValue = calculatePValue(zScore);

  // Effect size (Cohen's h)
  const effectSize = calculateCohenH(controlRate, variantRate);
  const effectSizeInterpretation = interpretEffectSize(effectSize);

  // Determine significance
  const alpha = getAlpha(confidenceLevel);
  const isSignificant = pValue < alpha;

  // Calculate statistical power
  const totalSampleSize = controlTotal + variantTotal;
  const statisticalPower = calculatePower(
    controlRate,
    variantRate,
    controlTotal,
    variantTotal,
    alpha
  );

  // Calculate minimum sample size requirement
  const minimumSampleSize = calculateMinimumSampleSize(
    controlRate,
    effectSize,
    alpha,
    0.8 // target power of 80%
  );

  const minimumSampleSizeReached = totalSampleSize >= minimumSampleSize * 2;

  // Generate recommendation
  const recommendation = generateRecommendation(
    isSignificant,
    minimumSampleSizeReached,
    statisticalPower,
    pValue,
    absoluteDifference
  );

  return {
    chiSquare,
    zScore,
    pValue,
    degreesOfFreedom: 1, // 2x2 contingency table always has 1 degree of freedom
    isSignificant,
    confidenceLevel,
    controlRate,
    variantRate,
    absoluteDifference,
    relativeDifference,
    effectSize,
    effectSizeInterpretation,
    controlSampleSize: controlTotal,
    variantSampleSize: variantTotal,
    totalSampleSize,
    statisticalPower,
    recommendation,
    minimumSampleSizeReached,
  };
}

/**
 * Calculate chi-square statistic for 2x2 contingency table
 */
export function calculateChiSquare(
  controlTotal: number,
  controlConversions: number,
  variantTotal: number,
  variantConversions: number
): number {
  const controlNonConversions = controlTotal - controlConversions;
  const variantNonConversions = variantTotal - variantConversions;

  const n = controlTotal + variantTotal;
  const a = controlConversions;
  const b = variantConversions;
  const c = controlNonConversions;
  const d = variantNonConversions;

  // Yates' continuity correction for small samples
  const numerator = Math.abs(a * d - b * c) - (n / 2);
  const denominator = (a + b) * (c + d) * (a + c) * (b + d);

  if (denominator === 0) return 0;

  return (n * numerator * numerator) / denominator;
}

/**
 * Calculate z-score for comparing two proportions
 */
export function calculateZScore(
  p1: number,
  p2: number,
  n1: number,
  n2: number
): number {
  // Pooled proportion
  const pooledP = ((p1 * n1) + (p2 * n2)) / (n1 + n2);

  // Standard error using pooled proportion
  const standardError = Math.sqrt(pooledP * (1 - pooledP) * (1/n1 + 1/n2));

  if (standardError === 0) return 0;

  return (p2 - p1) / standardError;
}

/**
 * Calculate p-value from z-score (two-tailed test)
 */
export function calculatePValue(zScore: number): number {
  const absZ = Math.abs(zScore);

  // Approximation of cumulative distribution function
  const p = normalCDF(absZ);

  // Two-tailed test
  return 2 * (1 - p);
}

/**
 * Calculate confidence interval for proportion difference
 */
export function calculateConfidenceInterval(
  p1: number,
  p2: number,
  n1: number,
  n2: number,
  confidenceLevel: 90 | 95 | 99 = 95
): ConfidenceInterval {
  const difference = p2 - p1;

  // Standard error for difference in proportions
  const standardError = Math.sqrt((p1 * (1 - p1) / n1) + (p2 * (1 - p2) / n2));

  // Critical value for confidence level
  const zCritical = getZCritical(confidenceLevel);

  // Margin of error
  const marginOfError = zCritical * standardError;

  return {
    lower: difference - marginOfError,
    upper: difference + marginOfError,
    confidenceLevel,
  };
}

/**
 * Calculate Cohen's h effect size for proportion differences
 */
export function calculateCohenH(p1: number, p2: number): number {
  // Arcsine transformation
  const phi1 = 2 * Math.asin(Math.sqrt(p1));
  const phi2 = 2 * Math.asin(Math.sqrt(p2));

  return Math.abs(phi2 - phi1);
}

/**
 * Calculate statistical power for current test
 */
export function calculatePower(
  p1: number,
  p2: number,
  n1: number,
  n2: number,
  alpha: number = 0.05
): number {
  // Effect size
  const h = calculateCohenH(p1, p2);

  // Calculate non-centrality parameter
  const nHarmonic = (2 * n1 * n2) / (n1 + n2); // harmonic mean
  const delta = h * Math.sqrt(nHarmonic / 2);

  // Critical value
  const zAlpha = getZCritical(alphaToConfidenceLevel(alpha));

  // Power calculation (simplified approximation)
  const power = normalCDF(delta - zAlpha);

  return Math.min(Math.max(power, 0), 1);
}

/**
 * Calculate minimum sample size needed per variant
 */
export function calculateMinimumSampleSize(
  baselineRate: number,
  minimumDetectableEffect: number,
  alpha: number = 0.05,
  power: number = 0.8
): number {
  const zAlpha = getZCritical(alphaToConfidenceLevel(alpha));
  const zBeta = getZCritical(powerToConfidenceLevel(power));

  const p1 = baselineRate;
  const p2 = baselineRate + minimumDetectableEffect;

  const pooledP = (p1 + p2) / 2;

  const numerator = Math.pow(zAlpha + zBeta, 2) * 2 * pooledP * (1 - pooledP);
  const denominator = Math.pow(p2 - p1, 2);

  if (denominator === 0) return Infinity;

  return Math.ceil(numerator / denominator);
}

/**
 * Calculate sample size requirements for desired power and effect size
 */
export function calculateSampleSizeRequirements(
  baselineRate: number,
  minimumDetectableEffect: number,
  confidenceLevel: 90 | 95 | 99 = 95,
  power: number = 0.8
): SampleSizeRequirement {
  const alpha = getAlpha(confidenceLevel);
  const perVariant = calculateMinimumSampleSize(
    baselineRate,
    minimumDetectableEffect,
    alpha,
    power
  );

  return {
    minimumPerVariant: perVariant,
    minimumTotal: perVariant * 2,
    detectedEffectSize: minimumDetectableEffect,
    power,
    alpha,
  };
}

// ============================================================
// Helper Functions
// ============================================================

/**
 * Validate test inputs
 */
function validateInputs(
  controlTotal: number,
  controlConversions: number,
  variantTotal: number,
  variantConversions: number
): void {
  if (controlTotal <= 0 || variantTotal <= 0) {
    throw new Error('Sample sizes must be positive');
  }

  if (controlConversions < 0 || variantConversions < 0) {
    throw new Error('Conversions cannot be negative');
  }

  if (controlConversions > controlTotal) {
    throw new Error('Control conversions cannot exceed control total');
  }

  if (variantConversions > variantTotal) {
    throw new Error('Variant conversions cannot exceed variant total');
  }
}

/**
 * Get alpha (significance level) from confidence level
 */
function getAlpha(confidenceLevel: 90 | 95 | 99): number {
  switch (confidenceLevel) {
    case 90: return 0.10;
    case 95: return 0.05;
    case 99: return 0.01;
    default: return 0.05;
  }
}

/**
 * Get z-critical value for confidence level
 */
function getZCritical(confidenceLevel: number): number {
  // Common z-critical values for two-tailed tests
  switch (confidenceLevel) {
    case 90: return 1.645;
    case 95: return 1.96;
    case 99: return 2.576;
    case 80: return 1.282; // for power calculations
    default: return 1.96;
  }
}

/**
 * Convert alpha to confidence level
 */
function alphaToConfidenceLevel(alpha: number): 90 | 95 | 99 {
  if (alpha <= 0.01) return 99;
  if (alpha <= 0.05) return 95;
  return 90;
}

/**
 * Convert power to equivalent confidence level for z-score lookup
 */
function powerToConfidenceLevel(power: number): number {
  // Convert power to equivalent one-tailed confidence level
  // Power = 0.8 corresponds to z = 0.842 (approximately 80th percentile)
  if (power >= 0.95) return 95;
  if (power >= 0.8) return 80;
  return 80;
}

/**
 * Normal cumulative distribution function approximation
 */
function normalCDF(x: number): number {
  // Abramowitz and Stegun approximation
  const t = 1 / (1 + 0.2316419 * Math.abs(x));
  const d = 0.3989423 * Math.exp(-x * x / 2);
  const p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));

  return x > 0 ? 1 - p : p;
}

/**
 * Interpret effect size (Cohen's h)
 */
function interpretEffectSize(h: number): 'negligible' | 'small' | 'medium' | 'large' {
  const absH = Math.abs(h);

  if (absH < 0.2) return 'negligible';
  if (absH < 0.5) return 'small';
  if (absH < 0.8) return 'medium';
  return 'large';
}

/**
 * Generate recommendation based on test results
 */
function generateRecommendation(
  isSignificant: boolean,
  minimumSampleSizeReached: boolean,
  statisticalPower: number | undefined,
  pValue: number,
  absoluteDifference: number
): 'continue' | 'declare_winner' | 'stop_test' | 'insufficient_data' {
  // Check for insufficient data
  if (!minimumSampleSizeReached) {
    return 'insufficient_data';
  }

  // Check for clear winner with statistical significance
  if (isSignificant && statisticalPower && statisticalPower >= 0.8) {
    return 'declare_winner';
  }

  // If significant but low power, recommend continuing
  if (isSignificant && (!statisticalPower || statisticalPower < 0.8)) {
    return 'continue';
  }

  // If not significant but close (p < 0.15) and power is good, continue
  if (!isSignificant && pValue < 0.15 && statisticalPower && statisticalPower >= 0.8) {
    return 'continue';
  }

  // If not significant, low power, and minimal difference, stop
  if (!isSignificant && Math.abs(absoluteDifference) < 0.01) {
    return 'stop_test';
  }

  // Default: continue collecting data
  return 'continue';
}

// ============================================================
// Comparison and Analysis Functions
// ============================================================

/**
 * Compare multiple variants against control
 */
export function compareVariantsToControl(
  controlTotal: number,
  controlConversions: number,
  variants: Array<{ total: number; conversions: number; name?: string }>,
  confidenceLevel: 90 | 95 | 99 = 95
): Array<SignificanceTestResult & { variantName?: string }> {
  return variants.map((variant, index) => ({
    ...calculateSignificance(
      controlTotal,
      controlConversions,
      variant.total,
      variant.conversions,
      confidenceLevel
    ),
    variantName: variant.name || `Variant ${index + 1}`,
  }));
}

/**
 * Determine which variant is the winner
 */
export function determineWinner(
  results: SignificanceTestResult[]
): { winnerIndex: number; confidence: number } | null {
  // Find variant with highest conversion rate that is statistically significant
  let bestIndex = -1;
  let bestRate = -1;
  let bestPValue = 1;

  for (let i = 0; i < results.length; i++) {
    const result = results[i];

    if (result.isSignificant && result.variantRate > bestRate) {
      bestIndex = i;
      bestRate = result.variantRate;
      bestPValue = result.pValue;
    }
  }

  if (bestIndex === -1) {
    return null;
  }

  return {
    winnerIndex: bestIndex,
    confidence: (1 - bestPValue) * 100,
  };
}

/**
 * Calculate Bayesian credible interval (simple approximation)
 */
export function calculateBayesianCredibleInterval(
  conversions: number,
  total: number,
  credibilityLevel: number = 0.95
): ConfidenceInterval {
  // Using Beta distribution approximation
  // Prior: Beta(1, 1) - uniform prior
  const alpha = conversions + 1;
  const beta = total - conversions + 1;

  // Approximate credible interval using normal approximation
  const mean = alpha / (alpha + beta);
  const variance = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1));
  const stdDev = Math.sqrt(variance);

  const z = getZCritical(credibilityLevel * 100 as 90 | 95 | 99);

  return {
    lower: Math.max(0, mean - z * stdDev),
    upper: Math.min(1, mean + z * stdDev),
    confidenceLevel: credibilityLevel * 100,
  };
}
