"use client";

import { useState } from "react";
import {
  FlaskConical,
  ChevronDown,
  ChevronUp,
  Info,
  Plus,
  Play,
  Pause,
  CheckCircle2,
  Trash2,
  Edit3,
  TrendingUp,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { ABTestResults } from "./ABTestResults";

/**
 * Traffic split configuration
 */
export interface TrafficSplit {
  /** Variant identifier (A, B, C, etc.) */
  variant: string;
  /** Traffic weight (percentage) */
  weight: number;
}

/**
 * Test variant configuration
 */
export interface TestVariant {
  /** Variant identifier */
  id: string;
  /** Variant label (A, B, C, etc.) */
  label: string;
  /** Subject line for this variant */
  subject: string;
  /** Preview text (optional) */
  previewText?: string;
  /** Content modifications (optional) */
  contentModifications?: {
    tone?: "casual" | "professional" | "friendly";
    length?: "short" | "medium" | "long";
  };
}

/**
 * A/B test configuration
 */
export interface ABTest {
  /** Unique test identifier */
  id: string;
  /** Test name */
  name: string;
  /** Test description */
  description?: string;
  /** Test type */
  type: "subject_line" | "content" | "send_time" | "full_email";
  /** Test status */
  status: "draft" | "running" | "paused" | "completed";
  /** Test variants */
  variants: TestVariant[];
  /** Traffic allocation */
  trafficSplit: TrafficSplit[];
  /** Metric to optimize for */
  primaryMetric: "open_rate" | "click_rate" | "conversion_rate";
  /** Minimum sample size before declaring winner */
  minSampleSize?: number;
  /** Confidence level required (e.g., 0.95 for 95%) */
  confidenceLevel?: number;
  /** Created timestamp */
  createdAt: Date;
  /** Started timestamp */
  startedAt?: Date;
  /** Completed timestamp */
  completedAt?: Date;
  /** Winner variant ID (if completed) */
  winnerId?: string;
}

/**
 * ABTestManager Settings
 */
export interface ABTestSettings {
  /** Enable A/B testing */
  enabled: boolean;
  /** Active tests */
  tests: ABTest[];
}

/**
 * ABTestManager Props
 */
export interface ABTestManagerProps {
  /** Current A/B test settings */
  settings: ABTestSettings;
  /** Callback when settings are updated */
  onUpdateSettings: (settings: ABTestSettings) => void;
  /** Optional custom className */
  className?: string;
}

/**
 * ABTestManager Component
 *
 * Interface for creating and managing A/B tests for email sequences.
 *
 * Features:
 * - Toggle A/B testing on/off
 * - Create new tests with multiple variants
 * - Configure traffic split across variants
 * - Set primary optimization metric
 * - Start/pause/complete tests
 * - View test results with statistical significance
 * - Delete tests
 * - Support for different test types (subject, content, timing)
 *
 * @example
 * ```tsx
 * <ABTestManager
 *   settings={abTestSettings}
 *   onUpdateSettings={(settings) => setABTestSettings(settings)}
 * />
 * ```
 */
export function ABTestManager({
  settings,
  onUpdateSettings,
  className,
}: ABTestManagerProps) {
  const [expanded, setExpanded] = useState(settings.enabled);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTestId, setEditingTestId] = useState<string | null>(null);
  const [viewingResultsId, setViewingResultsId] = useState<string | null>(null);

  // New test form state
  const [newTestName, setNewTestName] = useState("");
  const [newTestDescription, setNewTestDescription] = useState("");
  const [newTestType, setNewTestType] = useState<ABTest["type"]>("subject_line");
  const [newTestMetric, setNewTestMetric] = useState<ABTest["primaryMetric"]>("open_rate");
  const [newTestVariants, setNewTestVariants] = useState<TestVariant[]>([
    {
      id: "variant-a",
      label: "A",
      subject: "",
      previewText: "",
    },
    {
      id: "variant-b",
      label: "B",
      subject: "",
      previewText: "",
    },
  ]);
  const [newTestTrafficSplit, setNewTestTrafficSplit] = useState<TrafficSplit[]>([
    { variant: "variant-a", weight: 50 },
    { variant: "variant-b", weight: 50 },
  ]);

  /**
   * Toggle A/B testing
   */
  const handleToggle = () => {
    const newValue = !settings.enabled;
    onUpdateSettings({
      ...settings,
      enabled: newValue,
    });
    setExpanded(newValue);
  };

  /**
   * Create new test
   */
  const handleCreateTest = () => {
    // Validate
    if (!newTestName.trim()) return;
    if (newTestVariants.some((v) => !v.subject.trim())) return;

    const newTest: ABTest = {
      id: `test-${Date.now()}`,
      name: newTestName,
      description: newTestDescription,
      type: newTestType,
      status: "draft",
      variants: newTestVariants,
      trafficSplit: newTestTrafficSplit,
      primaryMetric: newTestMetric,
      minSampleSize: 100,
      confidenceLevel: 0.95,
      createdAt: new Date(),
    };

    onUpdateSettings({
      ...settings,
      tests: [...settings.tests, newTest],
    });

    // Reset form
    setNewTestName("");
    setNewTestDescription("");
    setNewTestType("subject_line");
    setNewTestMetric("open_rate");
    setNewTestVariants([
      { id: "variant-a", label: "A", subject: "", previewText: "" },
      { id: "variant-b", label: "B", subject: "", previewText: "" },
    ]);
    setNewTestTrafficSplit([
      { variant: "variant-a", weight: 50 },
      { variant: "variant-b", weight: 50 },
    ]);
    setShowCreateForm(false);
  };

  /**
   * Update test status
   */
  const handleUpdateTestStatus = (
    testId: string,
    newStatus: ABTest["status"]
  ) => {
    onUpdateSettings({
      ...settings,
      tests: settings.tests.map((test) =>
        test.id === testId
          ? {
              ...test,
              status: newStatus,
              startedAt: newStatus === "running" ? new Date() : test.startedAt,
              completedAt:
                newStatus === "completed" ? new Date() : test.completedAt,
            }
          : test
      ),
    });
  };

  /**
   * Delete test
   */
  const handleDeleteTest = (testId: string) => {
    onUpdateSettings({
      ...settings,
      tests: settings.tests.filter((test) => test.id !== testId),
    });
  };

  /**
   * Add variant to new test
   */
  const handleAddVariant = () => {
    const nextLabel = String.fromCharCode(65 + newTestVariants.length); // A, B, C, etc.
    const newVariant: TestVariant = {
      id: `variant-${nextLabel.toLowerCase()}`,
      label: nextLabel,
      subject: "",
      previewText: "",
    };

    setNewTestVariants([...newTestVariants, newVariant]);

    // Update traffic split to be equal
    const equalWeight = Math.floor(100 / (newTestVariants.length + 1));
    const remainder = 100 - equalWeight * (newTestVariants.length + 1);
    setNewTestTrafficSplit([
      ...newTestVariants.map((v, i) => ({
        variant: v.id,
        weight: equalWeight + (i === 0 ? remainder : 0),
      })),
      { variant: newVariant.id, weight: equalWeight },
    ]);
  };

  /**
   * Remove variant from new test
   */
  const handleRemoveVariant = (variantId: string) => {
    if (newTestVariants.length <= 2) return; // Minimum 2 variants

    setNewTestVariants(newTestVariants.filter((v) => v.id !== variantId));

    // Update traffic split
    const remainingVariants = newTestVariants.filter((v) => v.id !== variantId);
    const equalWeight = Math.floor(100 / remainingVariants.length);
    const remainder = 100 - equalWeight * remainingVariants.length;
    setNewTestTrafficSplit(
      remainingVariants.map((v, i) => ({
        variant: v.id,
        weight: equalWeight + (i === 0 ? remainder : 0),
      }))
    );
  };

  /**
   * Update variant
   */
  const handleUpdateVariant = (
    variantId: string,
    updates: Partial<TestVariant>
  ) => {
    setNewTestVariants(
      newTestVariants.map((v) =>
        v.id === variantId ? { ...v, ...updates } : v
      )
    );
  };

  /**
   * Update traffic split weight
   */
  const handleUpdateWeight = (variantId: string, weight: number) => {
    setNewTestTrafficSplit(
      newTestTrafficSplit.map((split) =>
        split.variant === variantId ? { ...split, weight } : split
      )
    );
  };

  /**
   * Get status badge color
   */
  const getStatusColor = (status: ABTest["status"]) => {
    switch (status) {
      case "running":
        return "bg-green-100 text-green-700";
      case "paused":
        return "bg-yellow-100 text-yellow-700";
      case "completed":
        return "bg-blue-100 text-blue-700";
      default:
        return "bg-slate-100 text-slate-700";
    }
  };

  return (
    <div className={cn("space-y-6", className)}>
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900">A/B Testing</h2>
        <p className="mt-1 text-sm text-slate-600">
          Test different email variants to optimize performance
        </p>
      </div>

      {/* Main Section */}
      <div className="rounded-lg border border-slate-200 bg-white">
        {/* Section Header */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex w-full items-center justify-between p-4 text-left transition-colors hover:bg-slate-50"
        >
          <div className="flex items-center gap-3">
            <div
              className={cn(
                "flex h-10 w-10 items-center justify-center rounded-lg",
                settings.enabled
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-600"
              )}
            >
              <FlaskConical className="h-5 w-5" />
            </div>
            <div>
              <div className="font-medium text-slate-900">
                A/B Test Experiments
              </div>
              <div className="text-sm text-slate-600">
                Test subject lines, content, and send times
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* Toggle Switch */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleToggle();
              }}
              className={cn(
                "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                settings.enabled ? "bg-slate-900" : "bg-slate-300"
              )}
            >
              <span
                className={cn(
                  "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                  settings.enabled ? "translate-x-6" : "translate-x-1"
                )}
              />
            </button>
            {/* Expand Icon */}
            {expanded ? (
              <ChevronUp className="h-5 w-5 text-slate-400" />
            ) : (
              <ChevronDown className="h-5 w-5 text-slate-400" />
            )}
          </div>
        </button>

        {/* Section Content */}
        {expanded && (
          <div className="border-t border-slate-200 p-4">
            {settings.enabled ? (
              <div className="space-y-6">
                {/* Active Tests */}
                {settings.tests.length > 0 && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-medium text-slate-900">
                        Your Tests
                      </h3>
                      <button
                        onClick={() => setShowCreateForm(!showCreateForm)}
                        className="flex items-center gap-1 rounded-md px-3 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100"
                      >
                        <Plus className="h-4 w-4" />
                        New Test
                      </button>
                    </div>

                    {settings.tests.map((test) => (
                      <div
                        key={test.id}
                        className="rounded-lg border border-slate-200 bg-white p-4"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <h4 className="font-medium text-slate-900">
                                {test.name}
                              </h4>
                              <span
                                className={cn(
                                  "rounded-full px-2 py-0.5 text-xs font-medium",
                                  getStatusColor(test.status)
                                )}
                              >
                                {test.status}
                              </span>
                            </div>
                            {test.description && (
                              <p className="mt-1 text-sm text-slate-600">
                                {test.description}
                              </p>
                            )}

                            {/* Test Details */}
                            <div className="mt-3 flex flex-wrap gap-4 text-sm text-slate-600">
                              <div>
                                <span className="font-medium">Type:</span>{" "}
                                {test.type.replace("_", " ")}
                              </div>
                              <div>
                                <span className="font-medium">Variants:</span>{" "}
                                {test.variants.length}
                              </div>
                              <div>
                                <span className="font-medium">Metric:</span>{" "}
                                {test.primaryMetric.replace("_", " ")}
                              </div>
                            </div>

                            {/* Variant Preview */}
                            <div className="mt-3 space-y-2">
                              {test.variants.map((variant, index) => {
                                const split = test.trafficSplit.find(
                                  (s) => s.variant === variant.id
                                );
                                return (
                                  <div
                                    key={variant.id}
                                    className="flex items-start gap-2 text-sm"
                                  >
                                    <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded bg-slate-100 text-xs font-medium text-slate-700">
                                      {variant.label}
                                    </span>
                                    <div className="flex-1">
                                      <div className="text-slate-900">
                                        {variant.subject}
                                      </div>
                                      {split && (
                                        <div className="text-xs text-slate-500">
                                          {split.weight}% traffic
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="flex items-center gap-1">
                            {test.status === "draft" && (
                              <button
                                onClick={() =>
                                  handleUpdateTestStatus(test.id, "running")
                                }
                                className="rounded-md p-1.5 text-green-600 transition-colors hover:bg-green-50"
                                title="Start test"
                              >
                                <Play className="h-4 w-4" />
                              </button>
                            )}
                            {test.status === "running" && (
                              <>
                                <button
                                  onClick={() =>
                                    setViewingResultsId(
                                      viewingResultsId === test.id
                                        ? null
                                        : test.id
                                    )
                                  }
                                  className="rounded-md p-1.5 text-blue-600 transition-colors hover:bg-blue-50"
                                  title="View results"
                                >
                                  <TrendingUp className="h-4 w-4" />
                                </button>
                                <button
                                  onClick={() =>
                                    handleUpdateTestStatus(test.id, "paused")
                                  }
                                  className="rounded-md p-1.5 text-yellow-600 transition-colors hover:bg-yellow-50"
                                  title="Pause test"
                                >
                                  <Pause className="h-4 w-4" />
                                </button>
                                <button
                                  onClick={() =>
                                    handleUpdateTestStatus(test.id, "completed")
                                  }
                                  className="rounded-md p-1.5 text-blue-600 transition-colors hover:bg-blue-50"
                                  title="Complete test"
                                >
                                  <CheckCircle2 className="h-4 w-4" />
                                </button>
                              </>
                            )}
                            {test.status === "paused" && (
                              <button
                                onClick={() =>
                                  handleUpdateTestStatus(test.id, "running")
                                }
                                className="rounded-md p-1.5 text-green-600 transition-colors hover:bg-green-50"
                                title="Resume test"
                              >
                                <Play className="h-4 w-4" />
                              </button>
                            )}
                            {test.status === "completed" && (
                              <button
                                onClick={() =>
                                  setViewingResultsId(
                                    viewingResultsId === test.id ? null : test.id
                                  )
                                }
                                className="rounded-md p-1.5 text-blue-600 transition-colors hover:bg-blue-50"
                                title="View results"
                              >
                                <TrendingUp className="h-4 w-4" />
                              </button>
                            )}
                            {test.status === "draft" && (
                              <button
                                onClick={() => handleDeleteTest(test.id)}
                                className="rounded-md p-1.5 text-red-600 transition-colors hover:bg-red-50"
                                title="Delete test"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Results Panel */}
                        {viewingResultsId === test.id && (
                          <div className="mt-4 border-t border-slate-200 pt-4">
                            <ABTestResults test={test} />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Create Test Form */}
                {(showCreateForm || settings.tests.length === 0) && (
                  <div className="rounded-lg border-2 border-slate-200 bg-slate-50 p-6">
                    <h3 className="mb-4 text-lg font-semibold text-slate-900">
                      Create New A/B Test
                    </h3>

                    <div className="space-y-4">
                      {/* Test Name */}
                      <div>
                        <label className="mb-1 block text-sm font-medium text-slate-700">
                          Test Name
                        </label>
                        <input
                          type="text"
                          value={newTestName}
                          onChange={(e) => setNewTestName(e.target.value)}
                          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                          placeholder="e.g., Subject Line Test - Welcome Email"
                        />
                      </div>

                      {/* Test Description */}
                      <div>
                        <label className="mb-1 block text-sm font-medium text-slate-700">
                          Description (Optional)
                        </label>
                        <textarea
                          value={newTestDescription}
                          onChange={(e) =>
                            setNewTestDescription(e.target.value)
                          }
                          rows={2}
                          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                          placeholder="What are you testing and why?"
                        />
                      </div>

                      {/* Test Type & Metric */}
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="mb-1 block text-sm font-medium text-slate-700">
                            Test Type
                          </label>
                          <select
                            value={newTestType}
                            onChange={(e) =>
                              setNewTestType(e.target.value as ABTest["type"])
                            }
                            className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                          >
                            <option value="subject_line">Subject Line</option>
                            <option value="content">Content</option>
                            <option value="send_time">Send Time</option>
                            <option value="full_email">Full Email</option>
                          </select>
                        </div>
                        <div>
                          <label className="mb-1 block text-sm font-medium text-slate-700">
                            Primary Metric
                          </label>
                          <select
                            value={newTestMetric}
                            onChange={(e) =>
                              setNewTestMetric(
                                e.target.value as ABTest["primaryMetric"]
                              )
                            }
                            className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                          >
                            <option value="open_rate">Open Rate</option>
                            <option value="click_rate">Click Rate</option>
                            <option value="conversion_rate">
                              Conversion Rate
                            </option>
                          </select>
                        </div>
                      </div>

                      {/* Variants */}
                      <div>
                        <div className="mb-2 flex items-center justify-between">
                          <label className="block text-sm font-medium text-slate-700">
                            Test Variants
                          </label>
                          <button
                            onClick={handleAddVariant}
                            className="flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-slate-700 transition-colors hover:bg-slate-200"
                          >
                            <Plus className="h-3 w-3" />
                            Add Variant
                          </button>
                        </div>

                        <div className="space-y-3">
                          {newTestVariants.map((variant) => {
                            const split = newTestTrafficSplit.find(
                              (s) => s.variant === variant.id
                            );
                            return (
                              <div
                                key={variant.id}
                                className="rounded-md border border-slate-300 bg-white p-3"
                              >
                                <div className="mb-2 flex items-center justify-between">
                                  <div className="flex items-center gap-2">
                                    <span className="flex h-6 w-6 items-center justify-center rounded bg-slate-900 text-xs font-bold text-white">
                                      {variant.label}
                                    </span>
                                    <span className="text-sm font-medium text-slate-900">
                                      Variant {variant.label}
                                    </span>
                                  </div>
                                  {newTestVariants.length > 2 && (
                                    <button
                                      onClick={() =>
                                        handleRemoveVariant(variant.id)
                                      }
                                      className="text-slate-400 transition-colors hover:text-red-600"
                                    >
                                      <Trash2 className="h-4 w-4" />
                                    </button>
                                  )}
                                </div>

                                <div className="space-y-2">
                                  <input
                                    type="text"
                                    value={variant.subject}
                                    onChange={(e) =>
                                      handleUpdateVariant(variant.id, {
                                        subject: e.target.value,
                                      })
                                    }
                                    className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                                    placeholder="Subject line"
                                  />
                                  <input
                                    type="text"
                                    value={variant.previewText || ""}
                                    onChange={(e) =>
                                      handleUpdateVariant(variant.id, {
                                        previewText: e.target.value,
                                      })
                                    }
                                    className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                                    placeholder="Preview text (optional)"
                                  />

                                  {/* Traffic Weight */}
                                  <div className="flex items-center gap-2">
                                    <label className="text-xs text-slate-600">
                                      Traffic:
                                    </label>
                                    <input
                                      type="number"
                                      min="0"
                                      max="100"
                                      value={split?.weight || 0}
                                      onChange={(e) =>
                                        handleUpdateWeight(
                                          variant.id,
                                          parseInt(e.target.value) || 0
                                        )
                                      }
                                      className="w-20 rounded-md border border-slate-300 px-2 py-1 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                                    />
                                    <span className="text-xs text-slate-600">
                                      %
                                    </span>
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>

                        {/* Traffic Split Warning */}
                        {newTestTrafficSplit.reduce(
                          (sum, split) => sum + split.weight,
                          0
                        ) !== 100 && (
                          <div className="mt-2 rounded-md border border-yellow-200 bg-yellow-50 p-2 text-xs text-yellow-800">
                            Traffic splits must add up to 100% (currently{" "}
                            {newTestTrafficSplit.reduce(
                              (sum, split) => sum + split.weight,
                              0
                            )}
                            %)
                          </div>
                        )}
                      </div>

                      {/* Action Buttons */}
                      <div className="flex items-center justify-end gap-2 pt-4">
                        {settings.tests.length > 0 && (
                          <button
                            onClick={() => setShowCreateForm(false)}
                            className="rounded-md px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-200"
                          >
                            Cancel
                          </button>
                        )}
                        <button
                          onClick={handleCreateTest}
                          disabled={
                            !newTestName.trim() ||
                            newTestVariants.some((v) => !v.subject.trim()) ||
                            newTestTrafficSplit.reduce(
                              (sum, split) => sum + split.weight,
                              0
                            ) !== 100
                          }
                          className={cn(
                            "rounded-md px-4 py-2 text-sm font-medium text-white transition-colors",
                            newTestName.trim() &&
                              !newTestVariants.some((v) => !v.subject.trim()) &&
                              newTestTrafficSplit.reduce(
                                (sum, split) => sum + split.weight,
                                0
                              ) === 100
                              ? "bg-slate-900 hover:bg-slate-800"
                              : "cursor-not-allowed bg-slate-400"
                          )}
                        >
                          Create Test
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* Info Box */}
                {settings.tests.length === 0 && !showCreateForm && (
                  <div className="rounded-lg bg-slate-50 p-8 text-center">
                    <FlaskConical className="mx-auto h-10 w-10 text-slate-400" />
                    <p className="mt-3 text-sm text-slate-600">
                      No A/B tests yet. Create your first test to start
                      optimizing email performance.
                    </p>
                    <button
                      onClick={() => setShowCreateForm(true)}
                      className="mt-4 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-800"
                    >
                      Create Your First Test
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="rounded-lg bg-slate-50 p-8 text-center">
                <Info className="mx-auto h-10 w-10 text-slate-400" />
                <p className="mt-3 text-sm text-slate-600">
                  Enable A/B testing to create experiments and optimize your
                  email performance
                </p>
                <button
                  onClick={handleToggle}
                  className="mt-4 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-800"
                >
                  Enable A/B Testing
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Summary Card */}
      {settings.enabled && settings.tests.length > 0 && (
        <div className="rounded-md border border-slate-200 bg-gradient-to-br from-slate-50 to-white p-4">
          <div className="text-sm text-slate-700">
            <span className="font-medium text-slate-900">
              Testing Summary:
            </span>
            <ul className="mt-2 space-y-1">
              <li className="flex items-center gap-2">
                <div className="h-1.5 w-1.5 rounded-full bg-slate-900" />
                <span>
                  {settings.tests.filter((t) => t.status === "running").length}{" "}
                  active test
                  {settings.tests.filter((t) => t.status === "running")
                    .length !== 1
                    ? "s"
                    : ""}
                </span>
              </li>
              <li className="flex items-center gap-2">
                <div className="h-1.5 w-1.5 rounded-full bg-slate-900" />
                <span>
                  {settings.tests.filter((t) => t.status === "completed")
                    .length}{" "}
                  completed test
                  {settings.tests.filter((t) => t.status === "completed")
                    .length !== 1
                    ? "s"
                    : ""}
                </span>
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
