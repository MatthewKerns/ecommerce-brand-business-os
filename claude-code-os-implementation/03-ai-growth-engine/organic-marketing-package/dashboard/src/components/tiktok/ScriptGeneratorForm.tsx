"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { Loader2, Sparkles, Package, Hash, Link2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAsyncState } from "@/hooks/useAsyncState";

interface ScriptGeneratorFormProps {
  channel: string;
  onScriptGenerated: (script: any) => void;
  isGenerating: boolean;
  setIsGenerating: (value: boolean) => void;
}

// Popular topics by channel
const topicSuggestions: Record<string, string[]> = {
  air: [
    "3-Second Deck Shuffle Technique",
    "5 Second Deck Check Before Tournament",
    "Quick Counter Strategy Guide",
    "Speed Sorting Your Collection",
    "Tournament Prep in 60 Seconds",
  ],
  water: [
    "My First Pokemon Card Story",
    "Collection Journey - 10 Years Later",
    "Finding My Childhood Binder",
    "Community Card Trading Experience",
    "Nostalgic Card Unboxing",
  ],
  earth: [
    "Perfect Card Storage System",
    "How to Organize 1000+ Cards",
    "Double Sleeve Protection Guide",
    "Binder vs Box Storage Comparison",
    "Card Condition Grading Tutorial",
  ],
  fire: [
    "Why Budget Decks Beat Meta",
    "Overrated Cards Everyone Uses",
    "Controversial Deck Building Opinion",
    "This Strategy Is Broken",
    "Hot Take: Ban This Card",
  ],
};

// Infinity Vault products
const products = [
  { id: "premium-binder", name: "Premium Card Binder", sku: "IVB-001" },
  { id: "deck-box", name: "Tournament Ready Deck Box", sku: "IVD-001" },
  { id: "sleeves", name: "Battle Ready Card Sleeves", sku: "IVS-001" },
  { id: "9-pocket", name: "9-Pocket Premium Pages", sku: "IVP-001" },
  { id: "collector-vault", name: "Collector's Vault Case", sku: "IVC-001" },
];

export function ScriptGeneratorForm({
  channel,
  onScriptGenerated,
  isGenerating,
  setIsGenerating,
}: ScriptGeneratorFormProps) {
  const [topic, setTopic] = useState("");
  const [selectedProduct, setSelectedProduct] = useState("");
  const [includeProductLink, setIncludeProductLink] = useState(false);
  const [additionalHashtags, setAdditionalHashtags] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);

  // Ref to hold current form values so the async function always reads fresh state
  const formRef = useRef({ channel, topic, selectedProduct, includeProductLink, additionalHashtags });
  formRef.current = { channel, topic, selectedProduct, includeProductLink, additionalHashtags };

  const generateScript = useCallback(
    async (signal: AbortSignal) => {
      const form = formRef.current;
      const response = await fetch("/api/tiktok/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal,
        body: JSON.stringify({
          channel_element: form.channel,
          topic: form.topic.trim(),
          product: form.selectedProduct || null,
          include_product_link: form.includeProductLink,
          additional_hashtags: form.additionalHashtags
            .split(",")
            .map((tag: string) => tag.trim())
            .filter(Boolean),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate script");
      }

      return response.json();
    },
    []
  );

  const {
    data: scriptData,
    error: asyncError,
    isLoading,
    refetch,
  } = useAsyncState({
    asyncFn: generateScript,
    immediate: false,
    retryCount: 1,
    retryDelay: 1000,
  });

  // Sync async state with parent component
  useEffect(() => {
    setIsGenerating(isLoading);
  }, [isLoading, setIsGenerating]);

  useEffect(() => {
    if (scriptData) {
      onScriptGenerated(scriptData);
    }
  }, [scriptData, onScriptGenerated]);

  const error = validationError || (asyncError?.message ?? null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (!topic.trim()) {
      setValidationError("Please enter a topic for your video");
      return;
    }

    await refetch();
  };

  const handleTopicSuggestion = (suggestion: string) => {
    setTopic(suggestion);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Topic Input */}
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Video Topic *
        </label>
        <textarea
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter your video topic or idea..."
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          rows={3}
          disabled={isGenerating}
        />

        {/* Topic Suggestions */}
        {topicSuggestions[channel] && (
          <div className="mt-2">
            <p className="mb-1 text-xs text-slate-600">Quick suggestions:</p>
            <div className="flex flex-wrap gap-2">
              {topicSuggestions[channel].slice(0, 3).map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => handleTopicSuggestion(suggestion)}
                  className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700 hover:bg-slate-200"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Product Selection */}
      <div>
        <label className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-700">
          <Package className="h-4 w-4" />
          Product Integration (Optional)
        </label>
        <select
          value={selectedProduct}
          onChange={(e) => setSelectedProduct(e.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          disabled={isGenerating}
        >
          <option value="">No product</option>
          {products.map((product) => (
            <option key={product.id} value={product.name}>
              {product.name} ({product.sku})
            </option>
          ))}
        </select>

        {/* Product Link Checkbox */}
        {selectedProduct && (
          <div className="mt-2 flex items-center gap-2">
            <input
              type="checkbox"
              id="includeLink"
              checked={includeProductLink}
              onChange={(e) => setIncludeProductLink(e.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              disabled={isGenerating}
            />
            <label
              htmlFor="includeLink"
              className="flex items-center gap-1 text-sm text-slate-700"
            >
              <Link2 className="h-3 w-3" />
              Include product link in video
            </label>
          </div>
        )}
      </div>

      {/* Additional Hashtags */}
      <div>
        <label className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-700">
          <Hash className="h-4 w-4" />
          Additional Hashtags (Optional)
        </label>
        <input
          type="text"
          value={additionalHashtags}
          onChange={(e) => setAdditionalHashtags(e.target.value)}
          placeholder="e.g., #Pokemon, #TCG, #CardGame (comma-separated)"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          disabled={isGenerating}
        />
      </div>

      {/* Error Display */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isGenerating || !topic.trim()}
        className={cn(
          "flex w-full items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors",
          isGenerating || !topic.trim()
            ? "cursor-not-allowed bg-slate-100 text-slate-400"
            : "bg-blue-600 text-white hover:bg-blue-700"
        )}
      >
        {isGenerating ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Generating Script...
          </>
        ) : (
          <>
            <Sparkles className="h-4 w-4" />
            Generate Video Script
          </>
        )}
      </button>

      {/* Tips */}
      <div className="rounded-lg bg-slate-50 p-3">
        <p className="text-xs font-medium text-slate-700">💡 Pro Tips:</p>
        <ul className="mt-1 space-y-1 text-xs text-slate-600">
          <li>• Be specific with your topic for better results</li>
          <li>• Product integration works best with Earth & Air channels</li>
          <li>• Keep Fire channel topics controversial but respectful</li>
          <li>• Water channel thrives on emotional connections</li>
        </ul>
      </div>
    </form>
  );
}