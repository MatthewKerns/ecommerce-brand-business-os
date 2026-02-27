"use client";

import { useState, useEffect } from "react";
import { Save, ArrowLeft, Play } from "lucide-react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  TemplateSelector,
  EmailTemplate,
  TEMPLATES,
} from "./TemplateSelector";
import { StepBuilder, SequenceStep } from "./StepBuilder";
import {
  PersonalizationEditor,
  PersonalizationSettings,
} from "./PersonalizationEditor";
import { ABTestManager, ABTestSettings } from "./ABTestManager";

/**
 * Sequence data for editing
 */
export interface Sequence {
  /** Unique identifier */
  id?: string;
  /** Sequence name */
  name: string;
  /** Sequence description */
  description: string;
  /** Status */
  status: "active" | "paused" | "draft";
  /** Template ID used (optional) */
  templateId?: string;
  /** Sequence steps */
  steps: SequenceStep[];
  /** Personalization settings (optional) */
  personalization?: PersonalizationSettings;
  /** A/B test settings (optional) */
  abTestSettings?: ABTestSettings;
}

/**
 * SequenceEditor Props
 */
export interface SequenceEditorProps {
  /** Existing sequence to edit (optional, for edit mode) */
  sequence?: Sequence;
  /** Callback when sequence is saved */
  onSave?: (sequence: Sequence) => void;
  /** Optional custom className */
  className?: string;
}

/**
 * Generate default steps from template
 */
function getTemplateSteps(templateId: string): SequenceStep[] {
  const template = TEMPLATES.find((t) => t.id === templateId);
  if (!template || template.id === "custom-sequence") {
    return [];
  }

  // Generate steps based on template preview
  return template.preview.subjects.map((subject, index) => ({
    id: `step-${Date.now()}-${index}`,
    name: template.preview.features[index] || `Email ${index + 1}`,
    subject: subject,
    previewText: "",
    delayDays: index === 0 ? 0 : index === 1 ? 2 : index === 2 ? 3 : 2,
    sendAtHour: 10,
    status: "draft" as const,
  }));
}

/**
 * SequenceEditor Component
 *
 * Main editor for creating and editing email sequences.
 *
 * Features:
 * - Template selection for quick start
 * - Sequence metadata (name, description, status)
 * - Step builder for managing email steps
 * - Personalization editor for source and interest variants
 * - Save and activate functionality
 * - Form validation
 * - Navigation controls
 *
 * @example
 * ```tsx
 * <SequenceEditor
 *   sequence={existingSequence}
 *   onSave={(seq) => console.log('Saved:', seq)}
 * />
 * ```
 */
export function SequenceEditor({
  sequence,
  onSave,
  className,
}: SequenceEditorProps) {
  const router = useRouter();

  // Editor state
  const [name, setName] = useState(sequence?.name || "");
  const [description, setDescription] = useState(sequence?.description || "");
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | undefined>(
    sequence?.templateId
  );
  const [steps, setSteps] = useState<SequenceStep[]>(sequence?.steps || []);
  const [status, setStatus] = useState<Sequence["status"]>(
    sequence?.status || "draft"
  );
  const [isSaving, setIsSaving] = useState(false);
  const [showTemplateSelector, setShowTemplateSelector] = useState(
    !sequence && steps.length === 0
  );
  const [personalization, setPersonalization] = useState<PersonalizationSettings>(
    sequence?.personalization || {
      enableSourcePersonalization: false,
      sourceVariants: [],
      enableInterestPersonalization: false,
      interestVariants: [],
      interestRules: [],
    }
  );
  const [abTestSettings, setAbTestSettings] = useState<ABTestSettings>(
    sequence?.abTestSettings || {
      enabled: false,
      tests: [],
    }
  );

  /**
   * Handle template selection
   */
  const handleSelectTemplate = (template: EmailTemplate) => {
    setSelectedTemplateId(template.id);

    // Auto-populate name and description if empty
    if (!name) {
      setName(template.name);
    }
    if (!description) {
      setDescription(template.description);
    }

    // Load template steps
    const templateSteps = getTemplateSteps(template.id);
    setSteps(templateSteps);

    // Hide template selector after selection
    setShowTemplateSelector(false);
  };

  /**
   * Handle save
   */
  const handleSave = async (newStatus?: Sequence["status"]) => {
    setIsSaving(true);

    const sequenceData: Sequence = {
      id: sequence?.id,
      name,
      description,
      status: newStatus || status,
      templateId: selectedTemplateId,
      steps,
      personalization,
      abTestSettings,
    };

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));

    if (onSave) {
      onSave(sequenceData);
    }

    setIsSaving(false);

    // Navigate back to sequences list
    router.push("/sequences");
  };

  /**
   * Handle save and activate
   */
  const handleSaveAndActivate = () => {
    handleSave("active");
  };

  /**
   * Validation
   */
  const isValid = name.trim() !== "" && steps.length > 0;

  return (
    <div className={cn("space-y-8", className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push("/sequences")}
            className="rounded-md p-2 text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">
              {sequence ? "Edit Sequence" : "Create New Sequence"}
            </h1>
            <p className="mt-1 text-sm text-slate-600">
              {sequence
                ? "Update your email sequence details"
                : "Set up an automated email sequence"}
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleSave("draft")}
            disabled={!isValid || isSaving}
            className={cn(
              "rounded-md px-4 py-2 text-sm font-medium transition-colors",
              isValid && !isSaving
                ? "bg-slate-200 text-slate-900 hover:bg-slate-300"
                : "cursor-not-allowed bg-slate-100 text-slate-400"
            )}
          >
            <Save className="mr-2 inline-block h-4 w-4" />
            Save Draft
          </button>
          <button
            onClick={handleSaveAndActivate}
            disabled={!isValid || isSaving}
            className={cn(
              "rounded-md px-4 py-2 text-sm font-medium text-white transition-colors",
              isValid && !isSaving
                ? "bg-slate-900 hover:bg-slate-800"
                : "cursor-not-allowed bg-slate-400"
            )}
          >
            <Play className="mr-2 inline-block h-4 w-4" />
            Save & Activate
          </button>
        </div>
      </div>

      {/* Sequence Metadata */}
      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="mb-4 text-xl font-bold text-slate-900">
          Sequence Details
        </h2>
        <div className="space-y-4">
          {/* Name */}
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              Sequence Name
              <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
              placeholder="e.g., Welcome Series"
            />
          </div>

          {/* Description */}
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
              placeholder="Describe what this sequence does..."
            />
          </div>

          {/* Template Info (if selected) */}
          {selectedTemplateId && selectedTemplateId !== "custom-sequence" && (
            <div className="rounded-md bg-slate-50 p-3">
              <p className="text-sm text-slate-700">
                <span className="font-medium">Template:</span>{" "}
                {TEMPLATES.find((t) => t.id === selectedTemplateId)?.name}
              </p>
              <button
                onClick={() => setShowTemplateSelector(true)}
                className="mt-2 text-sm text-slate-600 underline hover:text-slate-900"
              >
                Change template
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Template Selector (conditional) */}
      {showTemplateSelector && (
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <TemplateSelector
            selectedTemplateId={selectedTemplateId}
            onSelectTemplate={handleSelectTemplate}
          />
        </div>
      )}

      {/* Step Builder */}
      {!showTemplateSelector && (
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <StepBuilder steps={steps} onUpdateSteps={setSteps} />
        </div>
      )}

      {/* Personalization Editor */}
      {!showTemplateSelector && steps.length > 0 && (
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <PersonalizationEditor
            settings={personalization}
            onUpdateSettings={setPersonalization}
          />
        </div>
      )}

      {/* A/B Test Manager */}
      {!showTemplateSelector && steps.length > 0 && (
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <ABTestManager
            settings={abTestSettings}
            onUpdateSettings={setAbTestSettings}
          />
        </div>
      )}

      {/* Validation Message */}
      {!isValid && (
        <div className="rounded-md border border-yellow-200 bg-yellow-50 p-4">
          <p className="text-sm text-yellow-800">
            <span className="font-medium">Missing required fields:</span>
            {name.trim() === "" && " Sequence name"}
            {steps.length === 0 && " At least one email step"}
          </p>
        </div>
      )}

      {/* Bottom Action Bar (sticky) */}
      <div className="sticky bottom-0 z-10 border-t border-slate-200 bg-white/95 p-4 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <button
            onClick={() => router.push("/sequences")}
            className="text-sm text-slate-600 hover:text-slate-900"
          >
            Cancel
          </button>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleSave("draft")}
              disabled={!isValid || isSaving}
              className={cn(
                "rounded-md px-4 py-2 text-sm font-medium transition-colors",
                isValid && !isSaving
                  ? "bg-slate-200 text-slate-900 hover:bg-slate-300"
                  : "cursor-not-allowed bg-slate-100 text-slate-400"
              )}
            >
              Save Draft
            </button>
            <button
              onClick={handleSaveAndActivate}
              disabled={!isValid || isSaving}
              className={cn(
                "rounded-md px-4 py-2 text-sm font-medium text-white transition-colors",
                isValid && !isSaving
                  ? "bg-slate-900 hover:bg-slate-800"
                  : "cursor-not-allowed bg-slate-400"
              )}
            >
              Save & Activate
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
