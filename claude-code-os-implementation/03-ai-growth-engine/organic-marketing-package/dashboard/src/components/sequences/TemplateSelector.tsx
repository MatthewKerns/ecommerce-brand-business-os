"use client";

import { Mail, Clock, Check } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Email template option for selection
 */
export interface EmailTemplate {
  /** Unique identifier */
  id: string;
  /** Template name */
  name: string;
  /** Template description */
  description: string;
  /** Category: welcome or nurture */
  category: "welcome" | "nurture";
  /** Number of emails in template */
  emailCount: number;
  /** Timeline description (e.g., "7 days", "5 weeks") */
  timeline: string;
  /** Template preview details */
  preview: {
    /** Email subjects */
    subjects: string[];
    /** Key features */
    features: string[];
  };
}

/**
 * TemplateSelector Props
 */
export interface TemplateSelectorProps {
  /** Currently selected template ID */
  selectedTemplateId?: string;
  /** Callback when template is selected */
  onSelectTemplate: (template: EmailTemplate) => void;
  /** Optional custom className */
  className?: string;
}

/**
 * Pre-built email templates
 */
const TEMPLATES: EmailTemplate[] = [
  {
    id: "welcome-series",
    name: "Welcome Series",
    description: "4-email welcome sequence for new subscribers over 7 days",
    category: "welcome",
    emailCount: 4,
    timeline: "7 days",
    preview: {
      subjects: [
        "Welcome! Here's what to expect 👋",
        "The story behind our brand",
        "Real results from real customers",
        "Your exclusive first-time offer",
      ],
      features: [
        "Warm welcome with expectations",
        "Brand story and values",
        "Social proof and testimonials",
        "First purchase incentive",
      ],
    },
  },
  {
    id: "nurture-series",
    name: "Nurture Campaign",
    description: "4-email nurture sequence for non-buyers over 5 weeks",
    category: "nurture",
    emailCount: 4,
    timeline: "5 weeks",
    preview: {
      subjects: [
        "The ultimate guide to [topic]",
        "How [customer] achieved [result]",
        "Insider tips you won't find anywhere else",
        "Last chance: Special offer inside",
      ],
      features: [
        "Educational foundation",
        "Success stories and social proof",
        "Exclusive insights and value",
        "Conversion-focused offer",
      ],
    },
  },
  {
    id: "custom-sequence",
    name: "Custom Sequence",
    description: "Build your own sequence from scratch",
    category: "welcome",
    emailCount: 0,
    timeline: "Custom",
    preview: {
      subjects: ["Create your own email flow"],
      features: [
        "Full customization",
        "Add as many steps as needed",
        "Set your own timing",
        "Use AI to generate content",
      ],
    },
  },
];

/**
 * TemplateSelector Component
 *
 * Displays pre-built email templates for users to choose from when
 * creating a new sequence. Shows template details, email count, and timeline.
 *
 * Features:
 * - Template cards with preview information
 * - Category filtering (welcome vs nurture)
 * - Visual selection indicator
 * - Responsive grid layout
 * - Custom sequence option
 *
 * @example
 * ```tsx
 * <TemplateSelector
 *   selectedTemplateId="welcome-series"
 *   onSelectTemplate={(template) => console.log(template)}
 * />
 * ```
 */
export function TemplateSelector({
  selectedTemplateId,
  onSelectTemplate,
  className,
}: TemplateSelectorProps) {
  return (
    <div className={cn("space-y-6", className)}>
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900">
          Choose a Template
        </h2>
        <p className="mt-1 text-sm text-slate-600">
          Start with a proven template or build your own from scratch
        </p>
      </div>

      {/* Template Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {TEMPLATES.map((template) => {
          const isSelected = selectedTemplateId === template.id;

          return (
            <button
              key={template.id}
              onClick={() => onSelectTemplate(template)}
              className={cn(
                "group relative rounded-lg border-2 p-5 text-left transition-all hover:shadow-lg",
                isSelected
                  ? "border-slate-900 bg-slate-50 shadow-md"
                  : "border-slate-200 bg-white hover:border-slate-300"
              )}
            >
              {/* Selection Indicator */}
              {isSelected && (
                <div className="absolute right-3 top-3 flex h-6 w-6 items-center justify-center rounded-full bg-slate-900">
                  <Check className="h-4 w-4 text-white" />
                </div>
              )}

              {/* Icon */}
              <div
                className={cn(
                  "mb-3 inline-flex rounded-md p-2 transition-colors",
                  isSelected ? "bg-slate-900" : "bg-slate-100"
                )}
              >
                <Mail
                  className={cn(
                    "h-5 w-5",
                    isSelected ? "text-white" : "text-slate-600"
                  )}
                />
              </div>

              {/* Template Info */}
              <h3 className="mb-1 font-semibold text-slate-900">
                {template.name}
              </h3>
              <p className="mb-3 text-sm text-slate-600">
                {template.description}
              </p>

              {/* Meta Info */}
              <div className="mb-3 flex items-center gap-3 border-t border-slate-200 pt-3 text-xs text-slate-600">
                <div className="flex items-center gap-1">
                  <Mail className="h-3.5 w-3.5" />
                  <span>
                    {template.emailCount}{" "}
                    {template.emailCount === 1 ? "email" : "emails"}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  <span>{template.timeline}</span>
                </div>
              </div>

              {/* Preview Features */}
              <div className="space-y-1.5">
                {template.preview.features.slice(0, 3).map((feature, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-2 text-xs text-slate-600"
                  >
                    <div className="mt-0.5 h-1 w-1 flex-shrink-0 rounded-full bg-slate-400" />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
            </button>
          );
        })}
      </div>

      {/* Helper Text */}
      {selectedTemplateId && (
        <div className="rounded-md bg-slate-50 p-4">
          <p className="text-sm text-slate-700">
            <span className="font-medium">Next step:</span> Customize the email
            sequence below by adding, removing, or editing steps.
          </p>
        </div>
      )}
    </div>
  );
}

/**
 * Export templates for use in other components
 */
export { TEMPLATES };
