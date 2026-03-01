"use client";

import { Trash2, Plus, Edit2, Check, X } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

/**
 * Content variant for personalization
 */
export interface ContentVariant {
  /** Unique variant identifier */
  id: string;
  /** Variant name/label */
  name: string;
  /** Variant type (source or interest) */
  type: "source" | "interest";
  /** Variant value (e.g., 'social_media', 'ecommerce') */
  value: string;
  /** Custom subject line for this variant */
  subject?: string;
  /** Custom preview text for this variant */
  previewText?: string;
  /** Custom opening line for this variant */
  openingLine?: string;
  /** Tone adjustment (casual, professional, friendly) */
  tone?: "casual" | "professional" | "friendly";
}

/**
 * VariantManager Props
 */
export interface VariantManagerProps {
  /** Array of content variants */
  variants: ContentVariant[];
  /** Variant type filter */
  type: "source" | "interest";
  /** Callback when variants are updated */
  onUpdateVariants: (variants: ContentVariant[]) => void;
  /** Optional custom className */
  className?: string;
}

/**
 * Available source options
 */
const SOURCE_OPTIONS = [
  { value: "website", label: "Website Signup" },
  { value: "landing_page", label: "Landing Page" },
  { value: "social_media", label: "Social Media" },
  { value: "email_referral", label: "Email Referral" },
  { value: "partner", label: "Partner" },
  { value: "event", label: "Event" },
  { value: "manual", label: "Manual Entry" },
  { value: "import", label: "Import" },
  { value: "api", label: "API" },
  { value: "other", label: "Other" },
];

/**
 * Available interest options
 */
const INTEREST_OPTIONS = [
  { value: "ecommerce", label: "E-commerce" },
  { value: "content", label: "Content Marketing" },
  { value: "marketing", label: "Marketing" },
  { value: "tech", label: "Technology" },
  { value: "analytics", label: "Analytics" },
  { value: "automation", label: "Automation" },
  { value: "growth", label: "Growth" },
];

/**
 * Tone options
 */
const TONE_OPTIONS = [
  { value: "casual", label: "Casual" },
  { value: "professional", label: "Professional" },
  { value: "friendly", label: "Friendly" },
];

/**
 * VariantManager Component
 *
 * Manage content variants for personalization based on source or interest.
 *
 * Features:
 * - Add new variants with custom settings
 * - Edit existing variant details
 * - Delete variants
 * - Configure subject, preview text, opening line, and tone
 * - Visual variant cards with inline editing
 *
 * @example
 * ```tsx
 * <VariantManager
 *   variants={sourceVariants}
 *   type="source"
 *   onUpdateVariants={(variants) => setSourceVariants(variants)}
 * />
 * ```
 */
export function VariantManager({
  variants,
  type,
  onUpdateVariants,
  className,
}: VariantManagerProps) {
  const [editingVariantId, setEditingVariantId] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newVariantValue, setNewVariantValue] = useState("");

  const options = type === "source" ? SOURCE_OPTIONS : INTEREST_OPTIONS;

  /**
   * Add a new variant
   */
  const handleAddVariant = () => {
    if (!newVariantValue) return;

    const option = options.find((opt) => opt.value === newVariantValue);
    if (!option) return;

    const newVariant: ContentVariant = {
      id: `variant-${Date.now()}`,
      name: option.label,
      type,
      value: newVariantValue,
      subject: "",
      previewText: "",
      openingLine: "",
      tone: "friendly",
    };

    onUpdateVariants([...variants, newVariant]);
    setNewVariantValue("");
    setShowAddForm(false);
    setEditingVariantId(newVariant.id);
  };

  /**
   * Remove a variant
   */
  const handleRemoveVariant = (variantId: string) => {
    onUpdateVariants(variants.filter((v) => v.id !== variantId));
  };

  /**
   * Update a specific variant
   */
  const handleUpdateVariant = (
    variantId: string,
    updates: Partial<ContentVariant>
  ) => {
    onUpdateVariants(
      variants.map((variant) =>
        variant.id === variantId ? { ...variant, ...updates } : variant
      )
    );
  };

  /**
   * Toggle variant editing
   */
  const toggleEdit = (variantId: string) => {
    setEditingVariantId(editingVariantId === variantId ? null : variantId);
  };

  /**
   * Get available options (exclude already selected)
   */
  const availableOptions = options.filter(
    (opt) => !variants.some((v) => v.value === opt.value)
  );

  return (
    <div className={cn("space-y-4", className)}>
      {/* Variants List */}
      {variants.length === 0 ? (
        <div className="rounded-lg border-2 border-dashed border-slate-200 bg-slate-50 p-8 text-center">
          <p className="text-sm text-slate-600">
            No {type === "source" ? "source" : "interest"} variants yet. Add one
            to personalize content.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {variants.map((variant) => {
            const isEditing = editingVariantId === variant.id;

            return (
              <div
                key={variant.id}
                className={cn(
                  "rounded-lg border bg-white transition-all",
                  isEditing
                    ? "border-slate-900 shadow-md"
                    : "border-slate-200 hover:border-slate-300"
                )}
              >
                {/* Variant Header */}
                <div className="flex items-center justify-between p-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-900">
                        {variant.name}
                      </span>
                      <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                        {variant.value}
                      </span>
                    </div>
                    {!isEditing && variant.subject && (
                      <p className="mt-1 text-sm text-slate-600">
                        {variant.subject}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => toggleEdit(variant.id)}
                      className={cn(
                        "rounded-md p-1.5 transition-colors",
                        isEditing
                          ? "bg-slate-900 text-white hover:bg-slate-800"
                          : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                      )}
                    >
                      {isEditing ? (
                        <Check className="h-4 w-4" />
                      ) : (
                        <Edit2 className="h-4 w-4" />
                      )}
                    </button>
                    <button
                      onClick={() => handleRemoveVariant(variant.id)}
                      className="rounded-md p-1.5 text-slate-600 transition-colors hover:bg-red-50 hover:text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Editing Form */}
                {isEditing && (
                  <div className="border-t border-slate-200 bg-slate-50 p-3">
                    <div className="space-y-3">
                      {/* Subject Line */}
                      <div>
                        <label className="mb-1 block text-xs font-medium text-slate-700">
                          Custom Subject Line
                        </label>
                        <input
                          type="text"
                          value={variant.subject || ""}
                          onChange={(e) =>
                            handleUpdateVariant(variant.id, {
                              subject: e.target.value,
                            })
                          }
                          className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                          placeholder="e.g., Welcome from [Source]!"
                        />
                      </div>

                      {/* Preview Text */}
                      <div>
                        <label className="mb-1 block text-xs font-medium text-slate-700">
                          Custom Preview Text
                        </label>
                        <input
                          type="text"
                          value={variant.previewText || ""}
                          onChange={(e) =>
                            handleUpdateVariant(variant.id, {
                              previewText: e.target.value,
                            })
                          }
                          className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                          placeholder="Preview text for inbox"
                        />
                      </div>

                      {/* Opening Line */}
                      <div>
                        <label className="mb-1 block text-xs font-medium text-slate-700">
                          Custom Opening Line
                        </label>
                        <input
                          type="text"
                          value={variant.openingLine || ""}
                          onChange={(e) =>
                            handleUpdateVariant(variant.id, {
                              openingLine: e.target.value,
                            })
                          }
                          className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                          placeholder="e.g., Hey there, social media friend!"
                        />
                      </div>

                      {/* Tone */}
                      <div>
                        <label className="mb-1 block text-xs font-medium text-slate-700">
                          Tone
                        </label>
                        <select
                          value={variant.tone || "friendly"}
                          onChange={(e) =>
                            handleUpdateVariant(variant.id, {
                              tone: e.target.value as ContentVariant["tone"],
                            })
                          }
                          className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                        >
                          {TONE_OPTIONS.map((option) => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Add Variant Section */}
      {showAddForm ? (
        <div className="rounded-lg border border-slate-300 bg-white p-4">
          <div className="space-y-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Select {type === "source" ? "Source" : "Interest"}
              </label>
              <select
                value={newVariantValue}
                onChange={(e) => setNewVariantValue(e.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
              >
                <option value="">Choose an option...</option>
                {availableOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleAddVariant}
                disabled={!newVariantValue}
                className={cn(
                  "flex-1 rounded-md px-4 py-2 text-sm font-medium text-white transition-colors",
                  newVariantValue
                    ? "bg-slate-900 hover:bg-slate-800"
                    : "cursor-not-allowed bg-slate-400"
                )}
              >
                <Plus className="mr-2 inline-block h-4 w-4" />
                Add Variant
              </button>
              <button
                onClick={() => {
                  setShowAddForm(false);
                  setNewVariantValue("");
                }}
                className="rounded-md px-4 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100"
              >
                <X className="mr-2 inline-block h-4 w-4" />
                Cancel
              </button>
            </div>
          </div>
        </div>
      ) : (
        availableOptions.length > 0 && (
          <button
            onClick={() => setShowAddForm(true)}
            className="w-full rounded-lg border-2 border-dashed border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-colors hover:border-slate-400 hover:bg-slate-50 hover:text-slate-900"
          >
            <Plus className="mr-2 inline-block h-4 w-4" />
            Add {type === "source" ? "Source" : "Interest"} Variant
          </button>
        )
      )}

      {/* Summary */}
      {variants.length > 0 && (
        <div className="rounded-md bg-slate-50 p-3 text-xs text-slate-600">
          <span className="font-medium text-slate-900">{variants.length}</span>{" "}
          {type === "source" ? "source" : "interest"}{" "}
          {variants.length === 1 ? "variant" : "variants"} configured
        </div>
      )}
    </div>
  );
}
