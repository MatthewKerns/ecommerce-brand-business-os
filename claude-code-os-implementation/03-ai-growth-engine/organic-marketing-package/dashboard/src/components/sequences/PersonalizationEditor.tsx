"use client";

import { useState } from "react";
import { Users, Tag, ChevronDown, ChevronUp, Info } from "lucide-react";
import { cn } from "@/lib/utils";
import { VariantManager, ContentVariant } from "./VariantManager";

/**
 * Interest rule for personalization
 */
export interface InterestRule {
  /** Unique rule identifier */
  id: string;
  /** Interest category */
  interest: string;
  /** Rule conditions */
  conditions: {
    /** Field to check (tags, segments, customFields) */
    field: "tags" | "segments" | "customFields";
    /** Operator (contains, equals) */
    operator: "contains" | "equals";
    /** Value to match */
    value: string;
  }[];
  /** Content modifications */
  modifications: {
    /** Subject line override */
    subject?: string;
    /** Tone adjustment */
    tone?: "casual" | "professional" | "friendly";
  };
}

/**
 * Personalization settings for a sequence
 */
export interface PersonalizationSettings {
  /** Enable source-based personalization */
  enableSourcePersonalization: boolean;
  /** Source variants */
  sourceVariants: ContentVariant[];
  /** Enable interest-based personalization */
  enableInterestPersonalization: boolean;
  /** Interest variants */
  interestVariants: ContentVariant[];
  /** Interest matching rules */
  interestRules: InterestRule[];
}

/**
 * PersonalizationEditor Props
 */
export interface PersonalizationEditorProps {
  /** Current personalization settings */
  settings: PersonalizationSettings;
  /** Callback when settings are updated */
  onUpdateSettings: (settings: PersonalizationSettings) => void;
  /** Optional custom className */
  className?: string;
}

/**
 * PersonalizationEditor Component
 *
 * Main interface for managing email personalization settings.
 *
 * Features:
 * - Toggle source-based personalization
 * - Manage source variants (website, social, partner, etc.)
 * - Toggle interest-based personalization
 * - Manage interest variants (ecommerce, tech, marketing, etc.)
 * - Configure interest matching rules
 * - Collapsible sections for better UX
 * - Visual feedback for enabled/disabled states
 *
 * @example
 * ```tsx
 * <PersonalizationEditor
 *   settings={personalizationSettings}
 *   onUpdateSettings={(settings) => setPersonalizationSettings(settings)}
 * />
 * ```
 */
export function PersonalizationEditor({
  settings,
  onUpdateSettings,
  className,
}: PersonalizationEditorProps) {
  const [sourceExpanded, setSourceExpanded] = useState(
    settings.enableSourcePersonalization
  );
  const [interestExpanded, setInterestExpanded] = useState(
    settings.enableInterestPersonalization
  );

  /**
   * Toggle source personalization
   */
  const handleToggleSource = () => {
    const newValue = !settings.enableSourcePersonalization;
    onUpdateSettings({
      ...settings,
      enableSourcePersonalization: newValue,
    });
    setSourceExpanded(newValue);
  };

  /**
   * Toggle interest personalization
   */
  const handleToggleInterest = () => {
    const newValue = !settings.enableInterestPersonalization;
    onUpdateSettings({
      ...settings,
      enableInterestPersonalization: newValue,
    });
    setInterestExpanded(newValue);
  };

  /**
   * Update source variants
   */
  const handleUpdateSourceVariants = (variants: ContentVariant[]) => {
    onUpdateSettings({
      ...settings,
      sourceVariants: variants,
    });
  };

  /**
   * Update interest variants
   */
  const handleUpdateInterestVariants = (variants: ContentVariant[]) => {
    onUpdateSettings({
      ...settings,
      interestVariants: variants,
    });
  };

  /**
   * Add interest rule
   */
  const handleAddInterestRule = (interest: string) => {
    const newRule: InterestRule = {
      id: `rule-${Date.now()}`,
      interest,
      conditions: [
        {
          field: "tags",
          operator: "contains",
          value: interest,
        },
      ],
      modifications: {
        tone: "friendly",
      },
    };

    onUpdateSettings({
      ...settings,
      interestRules: [...settings.interestRules, newRule],
    });
  };

  return (
    <div className={cn("space-y-6", className)}>
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900">Personalization</h2>
        <p className="mt-1 text-sm text-slate-600">
          Customize email content based on signup source and subscriber interests
        </p>
      </div>

      {/* Source-Based Personalization */}
      <div className="rounded-lg border border-slate-200 bg-white">
        {/* Section Header */}
        <button
          onClick={() => setSourceExpanded(!sourceExpanded)}
          className="flex w-full items-center justify-between p-4 text-left transition-colors hover:bg-slate-50"
        >
          <div className="flex items-center gap-3">
            <div
              className={cn(
                "flex h-10 w-10 items-center justify-center rounded-lg",
                settings.enableSourcePersonalization
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-600"
              )}
            >
              <Users className="h-5 w-5" />
            </div>
            <div>
              <div className="font-medium text-slate-900">
                Source-Based Variants
              </div>
              <div className="text-sm text-slate-600">
                Personalize by signup source (website, social, partner, etc.)
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* Toggle Switch */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleToggleSource();
              }}
              className={cn(
                "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                settings.enableSourcePersonalization
                  ? "bg-slate-900"
                  : "bg-slate-300"
              )}
            >
              <span
                className={cn(
                  "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                  settings.enableSourcePersonalization
                    ? "translate-x-6"
                    : "translate-x-1"
                )}
              />
            </button>
            {/* Expand Icon */}
            {sourceExpanded ? (
              <ChevronUp className="h-5 w-5 text-slate-400" />
            ) : (
              <ChevronDown className="h-5 w-5 text-slate-400" />
            )}
          </div>
        </button>

        {/* Section Content */}
        {sourceExpanded && (
          <div className="border-t border-slate-200 p-4">
            {settings.enableSourcePersonalization ? (
              <VariantManager
                variants={settings.sourceVariants}
                type="source"
                onUpdateVariants={handleUpdateSourceVariants}
              />
            ) : (
              <div className="rounded-lg bg-slate-50 p-8 text-center">
                <Info className="mx-auto h-10 w-10 text-slate-400" />
                <p className="mt-3 text-sm text-slate-600">
                  Enable source-based personalization to customize content based
                  on how subscribers signed up
                </p>
                <button
                  onClick={handleToggleSource}
                  className="mt-4 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-800"
                >
                  Enable Source Personalization
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Interest-Based Personalization */}
      <div className="rounded-lg border border-slate-200 bg-white">
        {/* Section Header */}
        <button
          onClick={() => setInterestExpanded(!interestExpanded)}
          className="flex w-full items-center justify-between p-4 text-left transition-colors hover:bg-slate-50"
        >
          <div className="flex items-center gap-3">
            <div
              className={cn(
                "flex h-10 w-10 items-center justify-center rounded-lg",
                settings.enableInterestPersonalization
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-600"
              )}
            >
              <Tag className="h-5 w-5" />
            </div>
            <div>
              <div className="font-medium text-slate-900">
                Interest-Based Variants
              </div>
              <div className="text-sm text-slate-600">
                Personalize by subscriber interests and preferences
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* Toggle Switch */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleToggleInterest();
              }}
              className={cn(
                "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                settings.enableInterestPersonalization
                  ? "bg-slate-900"
                  : "bg-slate-300"
              )}
            >
              <span
                className={cn(
                  "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                  settings.enableInterestPersonalization
                    ? "translate-x-6"
                    : "translate-x-1"
                )}
              />
            </button>
            {/* Expand Icon */}
            {interestExpanded ? (
              <ChevronUp className="h-5 w-5 text-slate-400" />
            ) : (
              <ChevronDown className="h-5 w-5 text-slate-400" />
            )}
          </div>
        </button>

        {/* Section Content */}
        {interestExpanded && (
          <div className="border-t border-slate-200 p-4">
            {settings.enableInterestPersonalization ? (
              <div className="space-y-4">
                <VariantManager
                  variants={settings.interestVariants}
                  type="interest"
                  onUpdateVariants={handleUpdateInterestVariants}
                />

                {/* Interest Rules Info */}
                {settings.interestVariants.length > 0 && (
                  <div className="rounded-md border border-blue-200 bg-blue-50 p-4">
                    <div className="flex gap-3">
                      <Info className="h-5 w-5 flex-shrink-0 text-blue-600" />
                      <div className="text-sm text-blue-900">
                        <p className="font-medium">How Interest Matching Works</p>
                        <p className="mt-1 text-blue-800">
                          Variants are automatically matched based on subscriber
                          tags, segments, and custom fields. For example, if a
                          subscriber has the "ecommerce" tag, they'll receive the
                          E-commerce variant.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="rounded-lg bg-slate-50 p-8 text-center">
                <Info className="mx-auto h-10 w-10 text-slate-400" />
                <p className="mt-3 text-sm text-slate-600">
                  Enable interest-based personalization to customize content
                  based on subscriber interests
                </p>
                <button
                  onClick={handleToggleInterest}
                  className="mt-4 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-800"
                >
                  Enable Interest Personalization
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Summary Card */}
      {(settings.enableSourcePersonalization ||
        settings.enableInterestPersonalization) && (
        <div className="rounded-md border border-slate-200 bg-gradient-to-br from-slate-50 to-white p-4">
          <div className="text-sm text-slate-700">
            <span className="font-medium text-slate-900">
              Personalization Summary:
            </span>
            <ul className="mt-2 space-y-1">
              {settings.enableSourcePersonalization && (
                <li className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-slate-900" />
                  <span>
                    {settings.sourceVariants.length} source{" "}
                    {settings.sourceVariants.length === 1 ? "variant" : "variants"}
                  </span>
                </li>
              )}
              {settings.enableInterestPersonalization && (
                <li className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-slate-900" />
                  <span>
                    {settings.interestVariants.length} interest{" "}
                    {settings.interestVariants.length === 1
                      ? "variant"
                      : "variants"}
                  </span>
                </li>
              )}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
