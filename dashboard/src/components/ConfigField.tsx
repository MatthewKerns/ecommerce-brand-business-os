"use client";

import { cn } from "@/lib/utils";
import { AlertCircle } from "lucide-react";

/**
 * ConfigField component provides a reusable form field for configuration forms
 *
 * Features:
 * - Supports text, textarea, select, and number input types
 * - Label with optional/required indicator
 * - Helper text for field descriptions
 * - Error state with error message display
 * - Disabled and loading states
 * - Consistent styling with Tailwind CSS
 * - Responsive design
 *
 * @example
 * ```tsx
 * <ConfigField
 *   id="api-key"
 *   label="API Key"
 *   type="text"
 *   value={apiKey}
 *   onChange={(e) => setApiKey(e.target.value)}
 *   placeholder="Enter your API key"
 *   required
 *   helperText="Your API key from the provider's dashboard"
 *   error={errors.apiKey}
 * />
 * ```
 */

export interface ConfigFieldProps {
  /** Unique identifier for the field */
  id: string;
  /** Label text displayed above the field */
  label: string;
  /** Input type - text, textarea, select, or number */
  type?: "text" | "textarea" | "select" | "number";
  /** Current field value */
  value: string | number;
  /** Change handler */
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  /** Placeholder text */
  placeholder?: string;
  /** Whether the field is required */
  required?: boolean;
  /** Whether the field is disabled */
  disabled?: boolean;
  /** Helper text displayed below the field */
  helperText?: string;
  /** Error message - if present, field shows error state */
  error?: string;
  /** Options for select type (array of {value, label}) */
  options?: Array<{ value: string; label: string }>;
  /** Optional custom className for wrapper */
  className?: string;
}

export function ConfigField({
  id,
  label,
  type = "text",
  value,
  onChange,
  placeholder,
  required = false,
  disabled = false,
  helperText,
  error,
  options,
  className,
}: ConfigFieldProps) {
  const hasError = Boolean(error);

  // Base input classes
  const inputClasses = cn(
    "w-full rounded-lg border px-3 py-2 text-sm transition-colors",
    "placeholder:text-slate-400",
    "focus:outline-none focus:ring-2",
    hasError
      ? "border-red-300 bg-red-50 text-red-900 focus:border-red-500 focus:ring-red-200"
      : "border-slate-300 bg-white text-slate-900 focus:border-blue-500 focus:ring-blue-200",
    disabled && "cursor-not-allowed bg-slate-50 text-slate-500"
  );

  return (
    <div className={cn("space-y-1.5", className)}>
      {/* Label */}
      <label
        htmlFor={id}
        className="flex items-center gap-1 text-sm font-medium text-slate-700"
      >
        {label}
        {required && <span className="text-red-500">*</span>}
      </label>

      {/* Input Field */}
      {type === "textarea" ? (
        <textarea
          id={id}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          disabled={disabled}
          rows={4}
          className={inputClasses}
        />
      ) : type === "select" ? (
        <select
          id={id}
          value={value}
          onChange={onChange}
          required={required}
          disabled={disabled}
          className={inputClasses}
        >
          <option value="">Select an option</option>
          {options?.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          id={id}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          disabled={disabled}
          className={inputClasses}
        />
      )}

      {/* Helper Text / Error Message */}
      {hasError ? (
        <div className="flex items-center gap-1.5 text-sm text-red-600">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      ) : helperText ? (
        <p className="text-sm text-slate-500">{helperText}</p>
      ) : null}
    </div>
  );
}
