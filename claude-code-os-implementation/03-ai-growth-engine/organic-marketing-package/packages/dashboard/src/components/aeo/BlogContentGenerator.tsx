"use client";

import { useState } from "react";
import {
  FileText,
  Sparkles,
  Target,
  Loader2,
  Copy,
  Download,
  CheckCircle2,
  Info,
} from "lucide-react";

type ContentTone = "authoritative" | "conversational" | "technical" | "educational";
type ContentLength = "short" | "medium" | "long";

interface GenerationConfig {
  topic: string;
  targetKeyword: string;
  tone: ContentTone;
  length: ContentLength;
  includeSchema: boolean;
  includeFAQ: boolean;
  optimizeForAI: boolean;
  targetPlatforms: string[];
}

interface GeneratedContent {
  title: string;
  metaDescription: string;
  outline: string[];
  seoScore: number;
  aeoScore: number;
  estimatedWordCount: number;
  faqItems: { question: string; answer: string }[];
}

const AI_PLATFORMS = ["ChatGPT", "Claude", "Perplexity", "Gemini"];

// Mock generated result
const mockGeneratedContent: GeneratedContent = {
  title: "The Complete Guide to E-commerce Analytics: Metrics That Drive Revenue Growth",
  metaDescription: "Learn which e-commerce analytics metrics matter most for revenue growth. Data-driven strategies for tracking, measuring, and optimizing your online store performance.",
  outline: [
    "What Are E-commerce Analytics and Why Do They Matter?",
    "Essential E-commerce Metrics Every Store Owner Should Track",
    "How to Set Up Your Analytics Dashboard",
    "Revenue Metrics: AOV, LTV, and Conversion Rate Optimization",
    "Customer Behavior Analytics: Understanding the Buyer Journey",
    "Marketing Attribution: Which Channels Drive Real Results?",
    "Advanced Analytics: Predictive Models and AI-Powered Insights",
    "Common Analytics Mistakes and How to Avoid Them",
  ],
  seoScore: 87,
  aeoScore: 82,
  estimatedWordCount: 2400,
  faqItems: [
    { question: "What is the most important e-commerce metric?", answer: "Customer Lifetime Value (LTV) is widely considered the most important e-commerce metric because it captures the total revenue a customer generates over their entire relationship with your brand." },
    { question: "How often should I review my analytics?", answer: "Review key metrics daily for anomaly detection, conduct weekly analysis for trend identification, and perform monthly deep-dives for strategic planning." },
    { question: "What analytics tools do e-commerce stores need?", answer: "At minimum, you need Google Analytics for traffic, your platform's built-in analytics for sales data, and a customer data platform for unified tracking across channels." },
  ],
};

export function BlogContentGenerator() {
  const [config, setConfig] = useState<GenerationConfig>({
    topic: "",
    targetKeyword: "",
    tone: "authoritative",
    length: "medium",
    includeSchema: true,
    includeFAQ: true,
    optimizeForAI: true,
    targetPlatforms: ["ChatGPT", "Claude", "Perplexity"],
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  const handleGenerate = () => {
    if (!config.topic.trim()) return;
    setIsGenerating(true);
    // Simulated generation - will call API when blog agent integration is ready
    setTimeout(() => {
      setGeneratedContent(mockGeneratedContent);
      setIsGenerating(false);
    }, 2000);
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const togglePlatform = (platform: string) => {
    setConfig((prev) => ({
      ...prev,
      targetPlatforms: prev.targetPlatforms.includes(platform)
        ? prev.targetPlatforms.filter((p) => p !== platform)
        : [...prev.targetPlatforms, platform],
    }));
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Configuration Panel */}
        <div className="space-y-4">
          <div className="rounded-lg border border-slate-200 bg-white p-5">
            <h3 className="mb-4 font-semibold text-slate-900">Content Configuration</h3>

            {/* Topic */}
            <div className="mb-4">
              <label className="mb-1.5 block text-sm font-medium text-slate-700">
                Topic / Title Idea
              </label>
              <input
                type="text"
                value={config.topic}
                onChange={(e) => setConfig((prev) => ({ ...prev, topic: e.target.value }))}
                placeholder="e.g., E-commerce Analytics Best Practices"
                className="w-full rounded-lg border border-slate-200 px-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-100"
              />
            </div>

            {/* Target Keyword */}
            <div className="mb-4">
              <label className="mb-1.5 block text-sm font-medium text-slate-700">
                Target Keyword
              </label>
              <input
                type="text"
                value={config.targetKeyword}
                onChange={(e) => setConfig((prev) => ({ ...prev, targetKeyword: e.target.value }))}
                placeholder="e.g., ecommerce analytics"
                className="w-full rounded-lg border border-slate-200 px-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-100"
              />
            </div>

            {/* Tone */}
            <div className="mb-4">
              <label className="mb-1.5 block text-sm font-medium text-slate-700">
                Content Tone
              </label>
              <div className="grid grid-cols-2 gap-2">
                {(["authoritative", "conversational", "technical", "educational"] as ContentTone[]).map(
                  (tone) => (
                    <button
                      key={tone}
                      onClick={() => setConfig((prev) => ({ ...prev, tone }))}
                      className={`rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
                        config.tone === tone
                          ? "border-purple-300 bg-purple-50 text-purple-900"
                          : "border-slate-200 text-slate-700 hover:bg-slate-50"
                      }`}
                    >
                      {tone.charAt(0).toUpperCase() + tone.slice(1)}
                    </button>
                  )
                )}
              </div>
            </div>

            {/* Length */}
            <div className="mb-4">
              <label className="mb-1.5 block text-sm font-medium text-slate-700">
                Content Length
              </label>
              <div className="grid grid-cols-3 gap-2">
                {([
                  { value: "short" as const, label: "Short", desc: "800-1200 words" },
                  { value: "medium" as const, label: "Medium", desc: "1500-2500 words" },
                  { value: "long" as const, label: "Long", desc: "3000+ words" },
                ]).map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setConfig((prev) => ({ ...prev, length: option.value }))}
                    className={`rounded-lg border px-3 py-2 text-left transition-colors ${
                      config.length === option.value
                        ? "border-purple-300 bg-purple-50"
                        : "border-slate-200 hover:bg-slate-50"
                    }`}
                  >
                    <div className={`text-sm font-medium ${
                      config.length === option.value ? "text-purple-900" : "text-slate-700"
                    }`}>{option.label}</div>
                    <div className="text-xs text-slate-500">{option.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* AEO Options */}
          <div className="rounded-lg border border-slate-200 bg-white p-5">
            <h3 className="mb-4 flex items-center gap-2 font-semibold text-slate-900">
              <Target className="h-4 w-4 text-purple-600" />
              AEO Optimization
            </h3>

            <div className="space-y-3">
              <label className="flex cursor-pointer items-center justify-between rounded-lg border border-slate-200 p-3 hover:bg-slate-50">
                <div>
                  <div className="text-sm font-medium text-slate-900">Optimize for AI Citations</div>
                  <div className="text-xs text-slate-500">Structure content for AI assistant extraction</div>
                </div>
                <input
                  type="checkbox"
                  checked={config.optimizeForAI}
                  onChange={(e) => setConfig((prev) => ({ ...prev, optimizeForAI: e.target.checked }))}
                  className="h-4 w-4 rounded border-slate-300 text-purple-600 focus:ring-purple-500"
                />
              </label>

              <label className="flex cursor-pointer items-center justify-between rounded-lg border border-slate-200 p-3 hover:bg-slate-50">
                <div>
                  <div className="text-sm font-medium text-slate-900">Include FAQ Schema</div>
                  <div className="text-xs text-slate-500">Auto-generate FAQ section with schema markup</div>
                </div>
                <input
                  type="checkbox"
                  checked={config.includeFAQ}
                  onChange={(e) => setConfig((prev) => ({ ...prev, includeFAQ: e.target.checked }))}
                  className="h-4 w-4 rounded border-slate-300 text-purple-600 focus:ring-purple-500"
                />
              </label>

              <label className="flex cursor-pointer items-center justify-between rounded-lg border border-slate-200 p-3 hover:bg-slate-50">
                <div>
                  <div className="text-sm font-medium text-slate-900">Structured Data Markup</div>
                  <div className="text-xs text-slate-500">Add Article, HowTo, and entity schemas</div>
                </div>
                <input
                  type="checkbox"
                  checked={config.includeSchema}
                  onChange={(e) => setConfig((prev) => ({ ...prev, includeSchema: e.target.checked }))}
                  className="h-4 w-4 rounded border-slate-300 text-purple-600 focus:ring-purple-500"
                />
              </label>
            </div>

            {/* Target Platforms */}
            <div className="mt-4">
              <label className="mb-2 block text-sm font-medium text-slate-700">Target AI Platforms</label>
              <div className="flex flex-wrap gap-2">
                {AI_PLATFORMS.map((platform) => (
                  <button
                    key={platform}
                    onClick={() => togglePlatform(platform)}
                    className={`rounded-full px-3 py-1 text-sm font-medium transition-colors ${
                      config.targetPlatforms.includes(platform)
                        ? "bg-purple-100 text-purple-900"
                        : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                  >
                    {platform}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !config.topic.trim()}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-purple-600 py-3 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50"
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Generating Citation-Optimized Content...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Generate AEO-Optimized Blog Post
              </>
            )}
          </button>
        </div>

        {/* Preview Panel */}
        <div className="space-y-4">
          {generatedContent ? (
            <>
              {/* Score Preview */}
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <h3 className="mb-3 font-semibold text-slate-900">Content Scores</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{generatedContent.seoScore}</div>
                    <div className="text-xs text-slate-500">SEO Score</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">{generatedContent.aeoScore}</div>
                    <div className="text-xs text-slate-500">AEO Score</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-slate-900">{generatedContent.estimatedWordCount.toLocaleString()}</div>
                    <div className="text-xs text-slate-500">Est. Words</div>
                  </div>
                </div>
              </div>

              {/* Generated Title */}
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <div className="mb-2 flex items-center justify-between">
                  <h3 className="font-semibold text-slate-900">Generated Title</h3>
                  <button
                    onClick={() => handleCopy(generatedContent.title, "title")}
                    className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-700"
                  >
                    {copied === "title" ? <CheckCircle2 className="h-3 w-3 text-green-600" /> : <Copy className="h-3 w-3" />}
                    {copied === "title" ? "Copied" : "Copy"}
                  </button>
                </div>
                <p className="text-sm text-slate-900">{generatedContent.title}</p>
              </div>

              {/* Meta Description */}
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <div className="mb-2 flex items-center justify-between">
                  <h3 className="font-semibold text-slate-900">Meta Description</h3>
                  <button
                    onClick={() => handleCopy(generatedContent.metaDescription, "meta")}
                    className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-700"
                  >
                    {copied === "meta" ? <CheckCircle2 className="h-3 w-3 text-green-600" /> : <Copy className="h-3 w-3" />}
                    {copied === "meta" ? "Copied" : "Copy"}
                  </button>
                </div>
                <p className="text-sm text-slate-600">{generatedContent.metaDescription}</p>
                <div className="mt-2 text-xs text-slate-400">
                  {generatedContent.metaDescription.length}/160 characters
                </div>
              </div>

              {/* Content Outline */}
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="font-semibold text-slate-900">Content Outline</h3>
                  <button
                    onClick={() => handleCopy(generatedContent.outline.join("\n"), "outline")}
                    className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-700"
                  >
                    {copied === "outline" ? <CheckCircle2 className="h-3 w-3 text-green-600" /> : <Copy className="h-3 w-3" />}
                    {copied === "outline" ? "Copied" : "Copy"}
                  </button>
                </div>
                <ol className="space-y-2">
                  {generatedContent.outline.map((section, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm">
                      <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-purple-100 text-xs font-medium text-purple-700">
                        {i + 1}
                      </span>
                      <span className="text-slate-700">{section}</span>
                    </li>
                  ))}
                </ol>
              </div>

              {/* FAQ Items */}
              {generatedContent.faqItems.length > 0 && (
                <div className="rounded-lg border border-slate-200 bg-white p-5">
                  <h3 className="mb-3 flex items-center gap-2 font-semibold text-slate-900">
                    <Info className="h-4 w-4 text-purple-600" />
                    Generated FAQ Items
                  </h3>
                  <div className="space-y-3">
                    {generatedContent.faqItems.map((faq, i) => (
                      <div key={i} className="rounded-lg border border-slate-100 p-3">
                        <div className="text-sm font-medium text-slate-900">{faq.question}</div>
                        <div className="mt-1 text-sm text-slate-600">{faq.answer}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center gap-3">
                <button className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-purple-600 py-2.5 text-sm font-medium text-white hover:bg-purple-700">
                  <FileText className="h-4 w-4" />
                  Generate Full Article
                </button>
                <button className="flex items-center gap-2 rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50">
                  <Download className="h-4 w-4" />
                  Export
                </button>
              </div>
            </>
          ) : (
            <div className="flex h-full min-h-[400px] items-center justify-center rounded-lg border border-dashed border-slate-300 bg-slate-50">
              <div className="text-center">
                <FileText className="mx-auto mb-3 h-12 w-12 text-slate-300" />
                <h3 className="text-sm font-medium text-slate-600">No Content Generated Yet</h3>
                <p className="mt-1 text-sm text-slate-500">
                  Configure your content settings and click Generate
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
