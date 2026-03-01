"use client";

import {
  Mail,
  Clock,
  ChevronUp,
  ChevronDown,
  Trash2,
  Plus,
  GripVertical,
  Settings,
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

/**
 * Email sequence step
 */
export interface SequenceStep {
  /** Unique step identifier */
  id: string;
  /** Step name/title */
  name: string;
  /** Email subject line */
  subject: string;
  /** Preview text */
  previewText?: string;
  /** Days to wait before sending (relative to previous step or enrollment) */
  delayDays: number;
  /** Hours to send at (0-23, optional) */
  sendAtHour?: number;
  /** Step status */
  status: "active" | "draft";
}

/**
 * StepBuilder Props
 */
export interface StepBuilderProps {
  /** Array of sequence steps */
  steps: SequenceStep[];
  /** Callback when steps are updated */
  onUpdateSteps: (steps: SequenceStep[]) => void;
  /** Optional custom className */
  className?: string;
}

/**
 * StepBuilder Component
 *
 * Drag-and-drop builder for creating and organizing email sequence steps.
 *
 * Features:
 * - Add new steps with timing configuration
 * - Reorder steps with up/down arrows
 * - Edit step details (subject, delay, timing)
 * - Delete steps
 * - Visual timeline with delay indicators
 * - Responsive layout
 *
 * @example
 * ```tsx
 * <StepBuilder
 *   steps={steps}
 *   onUpdateSteps={(newSteps) => setSteps(newSteps)}
 * />
 * ```
 */
export function StepBuilder({
  steps,
  onUpdateSteps,
  className,
}: StepBuilderProps) {
  const [editingStepId, setEditingStepId] = useState<string | null>(null);
  const [expandedStepId, setExpandedStepId] = useState<string | null>(null);

  /**
   * Add a new step to the sequence
   */
  const handleAddStep = () => {
    const newStep: SequenceStep = {
      id: `step-${Date.now()}`,
      name: `Email ${steps.length + 1}`,
      subject: "",
      previewText: "",
      delayDays: steps.length === 0 ? 0 : 2,
      sendAtHour: 10,
      status: "draft",
    };

    onUpdateSteps([...steps, newStep]);
    setExpandedStepId(newStep.id);
  };

  /**
   * Remove a step from the sequence
   */
  const handleRemoveStep = (stepId: string) => {
    onUpdateSteps(steps.filter((s) => s.id !== stepId));
  };

  /**
   * Move step up in the sequence
   */
  const handleMoveUp = (index: number) => {
    if (index === 0) return;
    const newSteps = [...steps];
    [newSteps[index - 1], newSteps[index]] = [
      newSteps[index],
      newSteps[index - 1],
    ];
    onUpdateSteps(newSteps);
  };

  /**
   * Move step down in the sequence
   */
  const handleMoveDown = (index: number) => {
    if (index === steps.length - 1) return;
    const newSteps = [...steps];
    [newSteps[index], newSteps[index + 1]] = [
      newSteps[index + 1],
      newSteps[index],
    ];
    onUpdateSteps(newSteps);
  };

  /**
   * Update a specific step
   */
  const handleUpdateStep = (
    stepId: string,
    updates: Partial<SequenceStep>
  ) => {
    onUpdateSteps(
      steps.map((step) =>
        step.id === stepId ? { ...step, ...updates } : step
      )
    );
  };

  /**
   * Toggle step expansion for editing
   */
  const toggleExpand = (stepId: string) => {
    setExpandedStepId(expandedStepId === stepId ? null : stepId);
  };

  /**
   * Calculate cumulative days from start
   */
  const getCumulativeDays = (index: number): number => {
    return steps.slice(0, index + 1).reduce((sum, step) => sum + step.delayDays, 0);
  };

  return (
    <div className={cn("space-y-6", className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">
            Sequence Steps
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Add and organize emails in your sequence
          </p>
        </div>
        <button
          onClick={handleAddStep}
          className="flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-800"
        >
          <Plus className="h-4 w-4" />
          Add Step
        </button>
      </div>

      {/* Steps List */}
      {steps.length === 0 ? (
        <div className="rounded-lg border-2 border-dashed border-slate-200 bg-slate-50 p-12 text-center">
          <Mail className="mx-auto h-12 w-12 text-slate-400" />
          <h3 className="mt-4 text-lg font-semibold text-slate-900">
            No steps yet
          </h3>
          <p className="mt-2 text-sm text-slate-600">
            Add your first email to start building your sequence
          </p>
          <button
            onClick={handleAddStep}
            className="mt-6 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-800"
          >
            Add First Step
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {steps.map((step, index) => {
            const isExpanded = expandedStepId === step.id;
            const cumulativeDays = getCumulativeDays(index);

            return (
              <div
                key={step.id}
                className={cn(
                  "rounded-lg border-2 bg-white transition-all",
                  isExpanded
                    ? "border-slate-900 shadow-lg"
                    : "border-slate-200 hover:border-slate-300"
                )}
              >
                {/* Step Header */}
                <div className="flex items-center gap-3 p-4">
                  {/* Drag Handle Visual */}
                  <div className="flex flex-col items-center gap-1">
                    <button
                      onClick={() => handleMoveUp(index)}
                      disabled={index === 0}
                      className={cn(
                        "rounded p-0.5 transition-colors",
                        index === 0
                          ? "cursor-not-allowed text-slate-300"
                          : "text-slate-400 hover:bg-slate-100 hover:text-slate-700"
                      )}
                    >
                      <ChevronUp className="h-4 w-4" />
                    </button>
                    <GripVertical className="h-4 w-4 text-slate-300" />
                    <button
                      onClick={() => handleMoveDown(index)}
                      disabled={index === steps.length - 1}
                      className={cn(
                        "rounded p-0.5 transition-colors",
                        index === steps.length - 1
                          ? "cursor-not-allowed text-slate-300"
                          : "text-slate-400 hover:bg-slate-100 hover:text-slate-700"
                      )}
                    >
                      <ChevronDown className="h-4 w-4" />
                    </button>
                  </div>

                  {/* Step Info */}
                  <button
                    onClick={() => toggleExpand(step.id)}
                    className="flex flex-1 items-center gap-3 text-left"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100">
                      <Mail className="h-5 w-5 text-slate-600" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-slate-900">
                        {step.name}
                      </div>
                      <div className="text-sm text-slate-600">
                        {step.subject || "No subject set"}
                      </div>
                    </div>
                  </button>

                  {/* Timing Info */}
                  <div className="flex items-center gap-2 text-sm text-slate-600">
                    <Clock className="h-4 w-4" />
                    <span>
                      {index === 0
                        ? "Immediately"
                        : `Day ${cumulativeDays}`}
                    </span>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => toggleExpand(step.id)}
                      className="rounded-md p-1.5 text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900"
                    >
                      <Settings className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleRemoveStep(step.id)}
                      className="rounded-md p-1.5 text-slate-600 transition-colors hover:bg-red-50 hover:text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Expanded Edit Form */}
                {isExpanded && (
                  <div className="border-t border-slate-200 bg-slate-50 p-4">
                    <div className="space-y-4">
                      {/* Step Name */}
                      <div>
                        <label className="mb-1 block text-sm font-medium text-slate-700">
                          Step Name
                        </label>
                        <input
                          type="text"
                          value={step.name}
                          onChange={(e) =>
                            handleUpdateStep(step.id, { name: e.target.value })
                          }
                          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                          placeholder="e.g., Welcome Email"
                        />
                      </div>

                      {/* Email Subject */}
                      <div>
                        <label className="mb-1 block text-sm font-medium text-slate-700">
                          Email Subject
                        </label>
                        <input
                          type="text"
                          value={step.subject}
                          onChange={(e) =>
                            handleUpdateStep(step.id, {
                              subject: e.target.value,
                            })
                          }
                          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                          placeholder="e.g., Welcome! Here's what to expect 👋"
                        />
                      </div>

                      {/* Preview Text */}
                      <div>
                        <label className="mb-1 block text-sm font-medium text-slate-700">
                          Preview Text
                        </label>
                        <input
                          type="text"
                          value={step.previewText || ""}
                          onChange={(e) =>
                            handleUpdateStep(step.id, {
                              previewText: e.target.value,
                            })
                          }
                          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                          placeholder="Preview text shown in inbox"
                        />
                      </div>

                      {/* Timing Settings */}
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="mb-1 block text-sm font-medium text-slate-700">
                            {index === 0 ? "Send Immediately" : "Wait Days"}
                          </label>
                          <input
                            type="number"
                            min="0"
                            value={step.delayDays}
                            onChange={(e) =>
                              handleUpdateStep(step.id, {
                                delayDays: parseInt(e.target.value) || 0,
                              })
                            }
                            disabled={index === 0}
                            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900 disabled:bg-slate-100 disabled:text-slate-500"
                          />
                        </div>
                        <div>
                          <label className="mb-1 block text-sm font-medium text-slate-700">
                            Send At Hour (Optional)
                          </label>
                          <input
                            type="number"
                            min="0"
                            max="23"
                            value={step.sendAtHour || ""}
                            onChange={(e) =>
                              handleUpdateStep(step.id, {
                                sendAtHour: e.target.value
                                  ? parseInt(e.target.value)
                                  : undefined,
                              })
                            }
                            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                            placeholder="10"
                          />
                        </div>
                      </div>

                      {/* Helper Text */}
                      <div className="rounded-md bg-white p-3 text-xs text-slate-600">
                        {index === 0 ? (
                          <p>
                            This email will be sent immediately when someone is
                            enrolled in the sequence.
                          </p>
                        ) : (
                          <p>
                            This email will be sent{" "}
                            <span className="font-medium text-slate-900">
                              {step.delayDays} days
                            </span>{" "}
                            after the previous step
                            {step.sendAtHour !== undefined &&
                              ` at ${step.sendAtHour}:00`}
                            . Total time from start:{" "}
                            <span className="font-medium text-slate-900">
                              Day {cumulativeDays}
                            </span>
                            .
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Summary */}
      {steps.length > 0 && (
        <div className="rounded-md bg-slate-50 p-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-600">
              <span className="font-medium text-slate-900">
                {steps.length}
              </span>{" "}
              {steps.length === 1 ? "step" : "steps"} in this sequence
            </span>
            <span className="text-slate-600">
              Duration:{" "}
              <span className="font-medium text-slate-900">
                {getCumulativeDays(steps.length - 1)} days
              </span>
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
