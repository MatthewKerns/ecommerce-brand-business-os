"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import {
  Video,
  Loader2,
  Play,
  Download,
  CheckCircle,
  AlertCircle,
  Sparkles,
  Zap,
  Film,
  Palette,
} from "lucide-react";
import { useAsyncState } from "@/hooks/useAsyncState";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

interface VideoGeneratorProps {
  script: any;
  channel: string;
}

type VideoQuality = "low" | "standard" | "high" | "ultra";
type VideoStatus = "idle" | "processing" | "completed" | "failed";
type VideoProvider = "mock" | "remotion" | "runway" | "synthesia" | "ffmpeg";

interface VideoResult {
  id: string;
  status: VideoStatus;
  url?: string;
  thumbnailUrl?: string;
  duration?: number;
  provider?: string;
  error?: string;
}

const channelColors = {
  air: "border-sky-300 bg-sky-50",
  water: "border-blue-300 bg-blue-50",
  earth: "border-emerald-300 bg-emerald-50",
  fire: "border-orange-300 bg-orange-50",
};

const qualityOptions = [
  { value: "low", label: "Low (480p)", description: "Fast generation" },
  { value: "standard", label: "Standard (720p)", description: "Balanced" },
  { value: "high", label: "High (1080p)", description: "High quality" },
  { value: "ultra", label: "Ultra (4K)", description: "Maximum quality" },
];

const providerInfo = {
  mock: {
    name: "Mock Provider",
    description: "Test generation (JSON output)",
    icon: "🧪",
    capabilities: ["fast", "testing"],
  },
  remotion: {
    name: "Remotion",
    description: "React-based video generation",
    icon: "⚛️",
    capabilities: ["programmatic", "animations"],
  },
  runway: {
    name: "RunwayML",
    description: "AI-powered video generation",
    icon: "🤖",
    capabilities: ["ai", "effects"],
  },
  synthesia: {
    name: "Synthesia",
    description: "AI avatar videos",
    icon: "👤",
    capabilities: ["avatars", "voiceover"],
  },
  ffmpeg: {
    name: "FFmpeg",
    description: "Local video processing",
    icon: "🎬",
    capabilities: ["local", "fast"],
  },
};

export function VideoGenerator({ script, channel }: VideoGeneratorProps) {
  const [quality, setQuality] = useState<VideoQuality>("standard");
  const [provider, setProvider] = useState<VideoProvider>("mock");
  const [status, setStatus] = useState<VideoStatus>("idle");
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"basic" | "advanced">("basic");
  const progressIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Ref to hold current values for the async function
  const optionsRef = useRef({ script, channel, quality, provider });
  optionsRef.current = { script, channel, quality, provider };

  const generateVideoFn = useCallback(
    async (signal: AbortSignal) => {
      const opts = optionsRef.current;
      const response = await fetch("/api/tiktok/generate-video", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal,
        body: JSON.stringify({
          script: opts.script,
          channel: opts.channel,
          quality: opts.quality,
          provider: opts.provider,
          options: { fastGeneration: opts.provider === "mock" },
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate video: ${response.statusText}`);
      }

      return response.json() as Promise<VideoResult>;
    },
    []
  );

  const {
    data: videoResult,
    error: asyncError,
    isLoading,
    refetch,
    setData: setVideoResult,
  } = useAsyncState<VideoResult>({
    asyncFn: generateVideoFn,
    immediate: false,
    retryCount: 1,
    retryDelay: 2000,
  });

  // Sync status and progress with async state
  useEffect(() => {
    if (isLoading && status !== "processing") {
      setStatus("processing");
      setError(null);
      setProgress(0);
      // Start progress simulation
      progressIntervalRef.current = setInterval(() => {
        setProgress((prev) => (prev >= 90 ? prev : prev + Math.random() * 15));
      }, 500);
    } else if (!isLoading && status === "processing") {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      if (asyncError) {
        setStatus("failed");
        setError(asyncError.message || "Failed to generate video");
        setProgress(0);
      } else if (videoResult) {
        setProgress(100);
        setStatus("completed");
      }
    }
  }, [isLoading, asyncError, videoResult, status]);

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, []);

  const generateVideo = async () => {
    if (!script) {
      setError("No script available. Please generate a script first.");
      return;
    }
    await refetch();
  };

  const downloadVideo = () => {
    if (videoResult?.url) {
      const link = document.createElement("a");
      link.href = videoResult.url;
      link.download = `tiktok-${channel}-${videoResult.id}.mp4`;
      link.click();
    }
  };

  const resetGenerator = () => {
    setStatus("idle");
    setProgress(0);
    setVideoResult(null);
    setError(null);
  };

  return (
    <Card className={`border-2 ${channelColors[channel as keyof typeof channelColors]}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Video className="h-5 w-5" />
          Video Generation
        </CardTitle>
        <CardDescription>
          Transform your script into a TikTok video
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Status Messages */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Generation Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {status === "completed" && videoResult && (
          <Alert className="border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertTitle className="text-green-900">Video Ready!</AlertTitle>
            <AlertDescription className="text-green-700">
              Your video has been generated successfully using {videoResult.provider}.
            </AlertDescription>
          </Alert>
        )}

        {/* Tabs */}
        <div className="border rounded-lg bg-white">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab("basic")}
              className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === "basic"
                  ? "bg-gray-50 border-b-2 border-blue-500 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Basic Settings
            </button>
            <button
              onClick={() => setActiveTab("advanced")}
              className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === "advanced"
                  ? "bg-gray-50 border-b-2 border-blue-500 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Advanced
            </button>
          </div>

          <div className="p-4">
            {activeTab === "basic" ? (
              <div className="space-y-4">
                {/* Quality Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Video Quality
                  </label>
                  <select
                    value={quality}
                    onChange={(e) => setQuality(e.target.value as VideoQuality)}
                    disabled={status === "processing"}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {qualityOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label} - {option.description}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Provider Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Video Provider
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {Object.entries(providerInfo).map(([key, info]) => (
                      <button
                        key={key}
                        onClick={() => setProvider(key as VideoProvider)}
                        disabled={status === "processing"}
                        className={`rounded-lg border-2 p-3 text-left transition-all ${
                          provider === key
                            ? "border-blue-500 bg-blue-50"
                            : "border-gray-200 hover:border-gray-300"
                        } ${status === "processing" ? "opacity-50 cursor-not-allowed" : ""}`}
                      >
                        <div className="flex items-start gap-2">
                          <span className="text-xl">{info.icon}</span>
                          <div className="flex-1">
                            <div className="font-medium text-sm">{info.name}</div>
                            <div className="text-xs text-gray-600 mt-0.5">
                              {info.description}
                            </div>
                            <div className="mt-1 flex gap-1 flex-wrap">
                              {info.capabilities.map((cap) => (
                                <Badge key={cap} variant="secondary" className="text-xs">
                                  {cap}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="rounded-lg bg-gray-50 p-4">
                  <h4 className="font-medium text-sm mb-2">Advanced Options</h4>
                  <div className="space-y-3 text-sm">
                    <label className="flex items-center gap-2">
                      <input type="checkbox" className="rounded" />
                      <span>Auto-generate captions</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="checkbox" className="rounded" defaultChecked />
                      <span>Add channel watermark</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="checkbox" className="rounded" defaultChecked />
                      <span>Include background music</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="checkbox" className="rounded" />
                      <span>Enable AI voiceover</span>
                    </label>
                  </div>
                </div>

                <div className="rounded-lg bg-gray-50 p-4">
                  <h4 className="font-medium text-sm mb-2">Visual Effects</h4>
                  <div className="grid grid-cols-2 gap-2">
                    <button className="flex items-center justify-center gap-1 px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-white transition-colors">
                      <Sparkles className="h-4 w-4" />
                      Transitions
                    </button>
                    <button className="flex items-center justify-center gap-1 px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-white transition-colors">
                      <Palette className="h-4 w-4" />
                      Filters
                    </button>
                    <button className="flex items-center justify-center gap-1 px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-white transition-colors">
                      <Film className="h-4 w-4" />
                      Animations
                    </button>
                    <button className="flex items-center justify-center gap-1 px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-white transition-colors">
                      <Zap className="h-4 w-4" />
                      Effects
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Progress Display */}
        {status === "processing" && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Generating video...</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
            <p className="text-xs text-gray-600">
              This may take 30-60 seconds depending on the provider and quality
            </p>
          </div>
        )}

        {/* Video Preview */}
        {status === "completed" && videoResult && (
          <div className="rounded-lg border border-gray-200 bg-white p-4">
            <div className="aspect-[9/16] bg-gray-100 rounded-lg flex items-center justify-center">
              {videoResult.thumbnailUrl ? (
                <img
                  src={videoResult.thumbnailUrl}
                  alt="Video thumbnail"
                  className="h-full w-full object-cover rounded-lg"
                />
              ) : (
                <div className="text-center">
                  <Video className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Video Preview</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Duration: {videoResult.duration || 30}s
                  </p>
                </div>
              )}
            </div>
            <div className="mt-3 flex gap-2">
              <button
                onClick={() => console.log("Preview video")}
                className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Play className="h-4 w-4" />
                Preview
              </button>
              <button
                onClick={downloadVideo}
                className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Download className="h-4 w-4" />
                Download
              </button>
            </div>
          </div>
        )}
      </CardContent>

      <CardFooter className="flex gap-2">
        {status === "idle" || status === "failed" ? (
          <button
            onClick={generateVideo}
            disabled={!script}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-colors ${
              !script
                ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                : "bg-blue-600 text-white hover:bg-blue-700"
            }`}
          >
            <Video className="h-4 w-4" />
            Generate Video
          </button>
        ) : status === "processing" ? (
          <button
            disabled
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-gray-100 text-gray-600 rounded-lg font-medium cursor-not-allowed"
          >
            <Loader2 className="h-4 w-4 animate-spin" />
            Generating...
          </button>
        ) : (
          <>
            <button
              onClick={resetGenerator}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Generate Another
            </button>
            <button
              onClick={() => console.log("Publish to TikTok")}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Publish to TikTok
            </button>
          </>
        )}
      </CardFooter>
    </Card>
  );
}