"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { ConfigField } from "./ConfigField";
import { cn } from "@/lib/utils";
import { Settings, Check, AlertCircle } from "lucide-react";
import { useAsyncState } from "@/hooks/useAsyncState";

/**
 * ServiceConfigForm component provides configuration forms for each service
 *
 * Features:
 * - Separate forms for TikTok, Blog, and Email services
 * - Form validation with error handling
 * - Save button with success/error feedback
 * - Loading state during save operations
 * - Responsive design with proper spacing
 * - Uses ConfigField for consistent field styling
 *
 * @example
 * ```tsx
 * <ServiceConfigForm
 *   service="tiktok"
 *   onSave={(config) => handleSaveConfig(config)}
 * />
 * ```
 */

export type ServiceType = "tiktok" | "blog" | "email";

export interface ServiceConfig {
  [key: string]: string | number;
}

export interface ServiceConfigFormProps {
  /** Type of service - tiktok, blog, or email */
  service: ServiceType;
  /** Initial configuration values */
  initialConfig?: ServiceConfig;
  /** Callback when form is saved */
  onSave?: (config: ServiceConfig) => Promise<void>;
  /** Optional custom className for wrapper */
  className?: string;
}

/**
 * Default configurations for each service
 */
const DEFAULT_CONFIGS: Record<ServiceType, ServiceConfig> = {
  tiktok: {
    apiKey: "",
    postingSchedule: "daily",
    maxVideosPerDay: "3",
    videoLength: "30",
    autoPost: "true",
  },
  blog: {
    platform: "",
    postingFrequency: "weekly",
    postsPerWeek: "2",
    wordCount: "800",
    seoOptimization: "true",
  },
  email: {
    provider: "",
    fromAddress: "",
    fromName: "",
    replyTo: "",
    emailsPerMonth: "4",
  },
};

/**
 * Service metadata
 */
const SERVICE_METADATA = {
  tiktok: {
    title: "TikTok API Settings",
    description: "Configure TikTok content automation and posting schedule",
    icon: Settings,
  },
  blog: {
    title: "Blog Engine Configuration",
    description: "Configure blog content generation and publishing settings",
    icon: Settings,
  },
  email: {
    title: "Email Automation Settings",
    description: "Configure email provider and sending preferences",
    icon: Settings,
  },
};

export function ServiceConfigForm({
  service,
  initialConfig,
  onSave,
  className,
}: ServiceConfigFormProps) {
  const [config, setConfig] = useState<ServiceConfig>(
    initialConfig || DEFAULT_CONFIGS[service]
  );
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saveSuccess, setSaveSuccess] = useState(false);

  const metadata = SERVICE_METADATA[service];
  const Icon = metadata.icon;

  // Ref to hold current config and onSave so the async function reads fresh values
  const saveRef = useRef({ config, onSave });
  saveRef.current = { config, onSave };

  const saveConfig = useCallback(
    async (_signal: AbortSignal) => {
      const { config: currentConfig, onSave: currentOnSave } = saveRef.current;
      if (currentOnSave) {
        await currentOnSave(currentConfig);
      } else {
        // Simulate API call for demo
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      return currentConfig;
    },
    []
  );

  const {
    error: asyncError,
    isLoading: isSaving,
    refetch: executeSave,
    data: savedData,
  } = useAsyncState<ServiceConfig>({
    asyncFn: saveConfig,
    immediate: false,
    retryCount: 1,
    retryDelay: 1000,
  });

  const saveError = asyncError?.message ?? null;

  // Show success message when save completes
  useEffect(() => {
    if (savedData && !asyncError) {
      setSaveSuccess(true);
      const timer = setTimeout(() => setSaveSuccess(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [savedData, asyncError]);

  // Handle field change
  const handleChange = (field: string) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setConfig((prev) => ({
      ...prev,
      [field]: e.target.value,
    }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  // Validate form
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (service === "tiktok") {
      if (!config.apiKey) newErrors.apiKey = "API Key is required";
      if (!config.postingSchedule) newErrors.postingSchedule = "Posting schedule is required";
      if (!config.maxVideosPerDay || Number(config.maxVideosPerDay) < 1) {
        newErrors.maxVideosPerDay = "Must be at least 1";
      }
    } else if (service === "blog") {
      if (!config.platform) newErrors.platform = "Platform is required";
      if (!config.postingFrequency) newErrors.postingFrequency = "Posting frequency is required";
      if (!config.postsPerWeek || Number(config.postsPerWeek) < 1) {
        newErrors.postsPerWeek = "Must be at least 1";
      }
    } else if (service === "email") {
      if (!config.provider) newErrors.provider = "Provider is required";
      if (!config.fromAddress) newErrors.fromAddress = "From address is required";
      if (!config.fromName) newErrors.fromName = "From name is required";
      // Email validation
      if (config.fromAddress && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(config.fromAddress))) {
        newErrors.fromAddress = "Invalid email address";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaveSuccess(false);

    if (!validate()) {
      return;
    }

    await executeSave();
  };

  return (
    <form onSubmit={handleSubmit} className={cn("space-y-6", className)}>
      {/* Header */}
      <div className="flex items-start gap-3">
        <div className="rounded-lg bg-blue-100 p-2">
          <Icon className="h-5 w-5 text-blue-700" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{metadata.title}</h3>
          <p className="text-sm text-slate-600">{metadata.description}</p>
        </div>
      </div>

      {/* TikTok Form Fields */}
      {service === "tiktok" && (
        <div className="space-y-4">
          <ConfigField
            id="tiktok-api-key"
            label="TikTok API Key"
            type="text"
            value={config.apiKey}
            onChange={handleChange("apiKey")}
            placeholder="Enter your TikTok API key"
            required
            helperText="Your API key from TikTok Developer Portal"
            error={errors.apiKey}
          />

          <ConfigField
            id="tiktok-posting-schedule"
            label="Posting Schedule"
            type="select"
            value={config.postingSchedule}
            onChange={handleChange("postingSchedule")}
            required
            options={[
              { value: "daily", label: "Daily" },
              { value: "every-other-day", label: "Every Other Day" },
              { value: "weekly", label: "Weekly" },
            ]}
            helperText="How often to post new videos"
            error={errors.postingSchedule}
          />

          <ConfigField
            id="tiktok-max-videos"
            label="Max Videos Per Day"
            type="number"
            value={config.maxVideosPerDay}
            onChange={handleChange("maxVideosPerDay")}
            placeholder="3"
            required
            helperText="Maximum number of videos to post per day"
            error={errors.maxVideosPerDay}
          />

          <ConfigField
            id="tiktok-video-length"
            label="Target Video Length (seconds)"
            type="number"
            value={config.videoLength}
            onChange={handleChange("videoLength")}
            placeholder="30"
            helperText="Preferred length for generated videos"
          />

          <ConfigField
            id="tiktok-auto-post"
            label="Auto-Post"
            type="select"
            value={config.autoPost}
            onChange={handleChange("autoPost")}
            options={[
              { value: "true", label: "Enabled" },
              { value: "false", label: "Disabled (Review First)" },
            ]}
            helperText="Automatically post videos or require manual approval"
          />
        </div>
      )}

      {/* Blog Form Fields */}
      {service === "blog" && (
        <div className="space-y-4">
          <ConfigField
            id="blog-platform"
            label="Blog Platform"
            type="select"
            value={config.platform}
            onChange={handleChange("platform")}
            required
            options={[
              { value: "wordpress", label: "WordPress" },
              { value: "medium", label: "Medium" },
              { value: "ghost", label: "Ghost" },
              { value: "custom", label: "Custom Platform" },
            ]}
            helperText="Choose your blogging platform"
            error={errors.platform}
          />

          <ConfigField
            id="blog-posting-frequency"
            label="Posting Frequency"
            type="select"
            value={config.postingFrequency}
            onChange={handleChange("postingFrequency")}
            required
            options={[
              { value: "daily", label: "Daily" },
              { value: "weekly", label: "Weekly" },
              { value: "bi-weekly", label: "Bi-weekly" },
              { value: "monthly", label: "Monthly" },
            ]}
            helperText="How often to publish new blog posts"
            error={errors.postingFrequency}
          />

          <ConfigField
            id="blog-posts-per-week"
            label="Posts Per Week"
            type="number"
            value={config.postsPerWeek}
            onChange={handleChange("postsPerWeek")}
            placeholder="2"
            required
            helperText="Number of posts to generate per week"
            error={errors.postsPerWeek}
          />

          <ConfigField
            id="blog-word-count"
            label="Target Word Count"
            type="number"
            value={config.wordCount}
            onChange={handleChange("wordCount")}
            placeholder="800"
            helperText="Average word count for blog posts"
          />

          <ConfigField
            id="blog-seo"
            label="SEO Optimization"
            type="select"
            value={config.seoOptimization}
            onChange={handleChange("seoOptimization")}
            options={[
              { value: "true", label: "Enabled" },
              { value: "false", label: "Disabled" },
            ]}
            helperText="Automatically optimize posts for search engines"
          />
        </div>
      )}

      {/* Email Form Fields */}
      {service === "email" && (
        <div className="space-y-4">
          <ConfigField
            id="email-provider"
            label="Email Provider"
            type="select"
            value={config.provider}
            onChange={handleChange("provider")}
            required
            options={[
              { value: "sendgrid", label: "SendGrid" },
              { value: "mailgun", label: "Mailgun" },
              { value: "ses", label: "Amazon SES" },
              { value: "mailchimp", label: "Mailchimp" },
            ]}
            helperText="Choose your email service provider"
            error={errors.provider}
          />

          <ConfigField
            id="email-from-address"
            label="From Email Address"
            type="text"
            value={config.fromAddress}
            onChange={handleChange("fromAddress")}
            placeholder="newsletter@example.com"
            required
            helperText="Email address that appears as sender"
            error={errors.fromAddress}
          />

          <ConfigField
            id="email-from-name"
            label="From Name"
            type="text"
            value={config.fromName}
            onChange={handleChange("fromName")}
            placeholder="Your Brand Name"
            required
            helperText="Name that appears as sender"
            error={errors.fromName}
          />

          <ConfigField
            id="email-reply-to"
            label="Reply-To Address"
            type="text"
            value={config.replyTo}
            onChange={handleChange("replyTo")}
            placeholder="support@example.com"
            helperText="Email address for replies (optional)"
          />

          <ConfigField
            id="email-frequency"
            label="Emails Per Month"
            type="number"
            value={config.emailsPerMonth}
            onChange={handleChange("emailsPerMonth")}
            placeholder="4"
            helperText="Target number of email campaigns per month"
          />
        </div>
      )}

      {/* Success/Error Messages */}
      {saveSuccess && (
        <div className="flex items-center gap-2 rounded-lg bg-green-50 p-3 text-sm text-green-700">
          <Check className="h-4 w-4" />
          <span>Configuration saved successfully!</span>
        </div>
      )}

      {saveError && (
        <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4" />
          <span>{saveError}</span>
        </div>
      )}

      {/* Save Button */}
      <div className="flex justify-end border-t border-slate-200 pt-4">
        <button
          type="submit"
          disabled={isSaving}
          className={cn(
            "flex items-center gap-2 rounded-lg px-6 py-2.5 text-sm font-medium text-white transition-colors",
            isSaving
              ? "cursor-not-allowed bg-blue-400"
              : "bg-blue-600 hover:bg-blue-700"
          )}
        >
          {isSaving ? (
            <>
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              <span>Saving...</span>
            </>
          ) : (
            <>
              <Check className="h-4 w-4" />
              <span>Save Configuration</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
}
