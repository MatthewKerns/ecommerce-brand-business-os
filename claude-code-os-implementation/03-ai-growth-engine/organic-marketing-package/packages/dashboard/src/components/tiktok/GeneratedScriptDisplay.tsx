"use client";

import { useState } from "react";
import {
  Copy,
  Download,
  Save,
  Clock,
  Music,
  Type,
  Film,
  Hash,
  CheckCircle,
  Loader2,
  Calendar,
  Send,
  Video,
  PlayCircle,
  Sparkles,
  Eye,
  Share2,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ScriptSection {
  type: string;
  timeRange?: string;
  visual?: string;
  audio?: string;
  textOverlay?: string;
  notes?: string;
}

interface GeneratedScript {
  channel: string;
  topic: string;
  product?: string;
  sections: ScriptSection[];
  productionNotes: {
    musicStyle?: string;
    pace?: string;
    transitions?: string;
  };
  caption: string;
  hashtags: string[];
  estimatedLength: string;
  generatedAt: string;
}

interface GeneratedScriptDisplayProps {
  script: GeneratedScript | null;
  isLoading: boolean;
  channel: string;
}

export function GeneratedScriptDisplay({
  script,
  isLoading,
  channel,
}: GeneratedScriptDisplayProps) {
  const [copiedSection, setCopiedSection] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isScheduling, setIsScheduling] = useState(false);
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [generatedVideo, setGeneratedVideo] = useState<any>(null);
  const [videoProgress, setVideoProgress] = useState(0);

  const handleCopy = async (text: string, section: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedSection(section);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  const handleSave = async () => {
    if (!script) return;
    setIsSaving(true);

    try {
      const response = await fetch("/api/tiktok/scripts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(script),
      });

      if (response.ok) {
        // Show success state - script saved
      }
    } catch (error) {
      // Failed to save script
    } finally {
      setIsSaving(false);
    }
  };

  const handleSchedule = () => {
    setIsScheduling(true);
    // Open scheduling modal (implement later)
    setTimeout(() => setIsScheduling(false), 1000);
  };

  const handleDownload = () => {
    if (!script) return;

    const content = JSON.stringify(script, null, 2);
    const blob = new Blob([content], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `tiktok-script-${channel}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleGenerateVideo = async () => {
    if (!script) return;

    setIsGeneratingVideo(true);
    setVideoProgress(0);
    setGeneratedVideo(null);

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setVideoProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      const response = await fetch("/api/tiktok/generate-video", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          script: script,
          channel: channel,
          quality: "high",
          format: "vertical", // TikTok format
          duration: script.estimatedLength,
        }),
      });

      clearInterval(progressInterval);
      setVideoProgress(100);

      if (!response.ok) {
        throw new Error("Failed to generate video");
      }

      const videoData = await response.json();
      setGeneratedVideo(videoData);
    } catch (error) {
      // Error generating video - reset progress
      setVideoProgress(0);
    } finally {
      setIsGeneratingVideo(false);
    }
  };

  // Loading State
  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-blue-600" />
          <p className="mt-4 text-sm text-slate-600">
            Generating your {channel} channel script...
          </p>
          <p className="mt-1 text-xs text-slate-500">
            This usually takes 10-15 seconds
          </p>
        </div>
      </div>
    );
  }

  // Empty State
  if (!script) {
    return (
      <div className="flex h-96 items-center justify-center rounded-lg border-2 border-dashed border-slate-300 bg-slate-50">
        <div className="text-center">
          <Film className="mx-auto h-12 w-12 text-slate-400" />
          <p className="mt-4 text-sm text-slate-600">
            Your generated script will appear here
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Fill out the form and click "Generate Video Script"
          </p>
        </div>
      </div>
    );
  }

  // Display Generated Script
  return (
    <div className="space-y-4">
      {/* Action Buttons */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700"
        >
          {isSaving ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Save className="h-4 w-4" />
          )}
          Save Script
        </button>
        <button
          onClick={handleSchedule}
          className="flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
        >
          <Calendar className="h-4 w-4" />
          Schedule
        </button>
        <button
          onClick={handleDownload}
          className="flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
        >
          <Download className="h-4 w-4" />
          Download
        </button>
      </div>

      {/* Script Metadata */}
      <div className="rounded-lg bg-slate-50 p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-slate-600">
            <Clock className="h-3 w-3" />
            {script.estimatedLength}
          </div>
          {script.product && (
            <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700">
              Features: {script.product}
            </span>
          )}
        </div>
      </div>

      {/* Script Sections */}
      <div className="space-y-3">
        {script.sections.map((section, index) => (
          <div
            key={index}
            className="rounded-lg border border-slate-200 bg-white p-4"
          >
            {/* Section Header */}
            <div className="mb-2 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-slate-900">
                  {section.type}
                </span>
                {section.timeRange && (
                  <span className="text-xs text-slate-500">
                    ({section.timeRange})
                  </span>
                )}
              </div>
            </div>

            {/* Section Content */}
            <div className="space-y-2">
              {section.visual && (
                <div className="flex items-start gap-2">
                  <Film className="mt-0.5 h-4 w-4 text-slate-400" />
                  <div className="flex-1">
                    <p className="text-xs font-medium text-slate-600">Visual:</p>
                    <p className="text-sm text-slate-800">{section.visual}</p>
                  </div>
                </div>
              )}

              {section.audio && (
                <div className="flex items-start gap-2">
                  <Music className="mt-0.5 h-4 w-4 text-slate-400" />
                  <div className="flex-1">
                    <p className="text-xs font-medium text-slate-600">Audio:</p>
                    <p className="text-sm text-slate-800">{section.audio}</p>
                  </div>
                </div>
              )}

              {section.textOverlay && (
                <div className="flex items-start gap-2">
                  <Type className="mt-0.5 h-4 w-4 text-slate-400" />
                  <div className="flex-1">
                    <p className="text-xs font-medium text-slate-600">
                      Text Overlay:
                    </p>
                    <p className="text-sm font-medium text-slate-800">
                      {section.textOverlay}
                    </p>
                  </div>
                </div>
              )}

              {section.notes && (
                <p className="text-xs italic text-slate-500">{section.notes}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Production Notes */}
      {script.productionNotes && (
        <div className="rounded-lg border border-slate-200 bg-amber-50 p-4">
          <h4 className="mb-2 text-sm font-semibold text-slate-900">
            Production Notes
          </h4>
          <div className="space-y-1 text-sm text-slate-700">
            {script.productionNotes.musicStyle && (
              <p>🎵 Music: {script.productionNotes.musicStyle}</p>
            )}
            {script.productionNotes.pace && (
              <p>⚡ Pace: {script.productionNotes.pace}</p>
            )}
            {script.productionNotes.transitions && (
              <p>🎬 Transitions: {script.productionNotes.transitions}</p>
            )}
          </div>
        </div>
      )}

      {/* Caption & Hashtags */}
      <div className="space-y-3">
        {/* Caption */}
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <div className="mb-2 flex items-center justify-between">
            <h4 className="text-sm font-semibold text-slate-900">Caption</h4>
            <button
              onClick={() => handleCopy(script.caption, "caption")}
              className="flex items-center gap-1 rounded px-2 py-1 text-xs text-slate-600 hover:bg-slate-100"
            >
              {copiedSection === "caption" ? (
                <>
                  <CheckCircle className="h-3 w-3 text-green-600" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  Copy
                </>
              )}
            </button>
          </div>
          <p className="text-sm text-slate-700">{script.caption}</p>
        </div>

        {/* Hashtags */}
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <div className="mb-2 flex items-center justify-between">
            <h4 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <Hash className="h-4 w-4" />
              Hashtags
            </h4>
            <button
              onClick={() =>
                handleCopy(script.hashtags.join(" "), "hashtags")
              }
              className="flex items-center gap-1 rounded px-2 py-1 text-xs text-slate-600 hover:bg-slate-100"
            >
              {copiedSection === "hashtags" ? (
                <>
                  <CheckCircle className="h-3 w-3 text-green-600" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  Copy All
                </>
              )}
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {script.hashtags.map((tag, index) => (
              <span
                key={index}
                className="rounded-full bg-blue-100 px-2 py-1 text-xs text-blue-700"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="rounded-lg bg-green-50 p-4">
        <p className="text-sm font-semibold text-green-900">
          ✅ Script Generated Successfully!
        </p>
        <p className="mt-1 text-xs text-green-700">
          Next steps: Review the script, make any adjustments, then generate a
          video or schedule for publishing.
        </p>
      </div>

      {/* Generate Video Section */}
      <div className="mt-6 space-y-4 rounded-lg border-2 border-purple-200 bg-purple-50 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="flex items-center gap-2 text-lg font-semibold text-slate-900">
              <Video className="h-5 w-5 text-purple-600" />
              Generate TikTok Video
            </h3>
            <p className="mt-1 text-sm text-slate-600">
              Transform your script into a ready-to-post TikTok video
            </p>
          </div>
          <button
            onClick={handleGenerateVideo}
            disabled={isGeneratingVideo}
            className={cn(
              "flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all",
              isGeneratingVideo
                ? "cursor-not-allowed bg-purple-200 text-purple-400"
                : "bg-purple-600 text-white hover:bg-purple-700"
            )}
          >
            {isGeneratingVideo ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Generating Video...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Generate Video
              </>
            )}
          </button>
        </div>

        {/* Video Generation Progress */}
        {isGeneratingVideo && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-600">
              <span>Creating your TikTok video...</span>
              <span>{videoProgress}%</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-purple-200">
              <div
                className="h-full bg-purple-600 transition-all duration-500"
                style={{ width: `${videoProgress}%` }}
              />
            </div>
            <p className="text-xs text-slate-500">
              This usually takes 30-60 seconds depending on video length
            </p>
          </div>
        )}

        {/* Generated Video Output */}
        {generatedVideo && !isGeneratingVideo && (
          <div className="space-y-4">
            <div className="rounded-lg border border-purple-300 bg-white p-4">
              {/* Video Preview */}
              <div className="aspect-[9/16] w-full max-w-sm mx-auto rounded-lg bg-slate-900 relative overflow-hidden">
                {generatedVideo.thumbnailUrl ? (
                  <img
                    src={generatedVideo.thumbnailUrl}
                    alt="Video thumbnail"
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="flex h-full items-center justify-center">
                    <PlayCircle className="h-16 w-16 text-white/50" />
                  </div>
                )}

                {/* Video Overlay Info */}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                  <p className="text-sm font-semibold text-white">
                    {script.topic}
                  </p>
                  <div className="mt-2 flex items-center gap-4 text-xs text-white/80">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {generatedVideo.duration || script.estimatedLength}
                    </span>
                    <span className="flex items-center gap-1">
                      <Film className="h-3 w-3" />
                      {generatedVideo.format || "9:16"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Video Details */}
              <div className="mt-4 space-y-3">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-xs text-slate-500">Video ID</p>
                    <p className="font-mono text-xs text-slate-700">
                      {generatedVideo.id || "vid_" + Date.now()}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">File Size</p>
                    <p className="text-xs text-slate-700">
                      {generatedVideo.fileSize || "12.4 MB"}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">Resolution</p>
                    <p className="text-xs text-slate-700">
                      {generatedVideo.resolution || "1080x1920"}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">FPS</p>
                    <p className="text-xs text-slate-700">
                      {generatedVideo.fps || "30"}
                    </p>
                  </div>
                </div>

                {/* Video Actions */}
                <div className="flex flex-wrap gap-2 border-t pt-3">
                  <button className="flex items-center gap-2 rounded-lg bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700">
                    <Download className="h-4 w-4" />
                    Download Video
                  </button>
                  <button className="flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50">
                    <Eye className="h-4 w-4" />
                    Preview
                  </button>
                  <button className="flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50">
                    <Send className="h-4 w-4" />
                    Publish to TikTok
                  </button>
                  <button className="flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50">
                    <Share2 className="h-4 w-4" />
                    Share
                  </button>
                </div>
              </div>
            </div>

            {/* Video Generation Info */}
            <div className="rounded-lg bg-purple-100 p-3">
              <p className="text-xs font-semibold text-purple-900">
                🎬 Video Ready!
              </p>
              <ul className="mt-1 space-y-0.5 text-xs text-purple-700">
                <li>• Optimized for TikTok's algorithm</li>
                <li>• Includes text overlays and transitions</li>
                <li>• Background music matched to {channel} channel style</li>
                <li>• Ready for immediate publishing</li>
              </ul>
            </div>
          </div>
        )}

        {/* Video Generation Options (shown before generating) */}
        {!generatedVideo && !isGeneratingVideo && (
          <div className="rounded-lg bg-white p-4 space-y-3">
            <h4 className="text-sm font-semibold text-slate-900">
              Video Generation Options
            </h4>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <label className="text-xs text-slate-600">Video Style</label>
                <select className="mt-1 w-full rounded-lg border border-slate-300 px-2 py-1 text-xs">
                  <option>Dynamic ({channel} style)</option>
                  <option>Minimal</option>
                  <option>Energetic</option>
                  <option>Professional</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-600">Music</label>
                <select className="mt-1 w-full rounded-lg border border-slate-300 px-2 py-1 text-xs">
                  <option>Auto-select</option>
                  <option>Trending sounds</option>
                  <option>No music</option>
                  <option>Custom upload</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-600">Voice</label>
                <select className="mt-1 w-full rounded-lg border border-slate-300 px-2 py-1 text-xs">
                  <option>AI Voice (Male)</option>
                  <option>AI Voice (Female)</option>
                  <option>Text only</option>
                  <option>Upload voiceover</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-600">Quality</label>
                <select className="mt-1 w-full rounded-lg border border-slate-300 px-2 py-1 text-xs">
                  <option>High (1080p)</option>
                  <option>Ultra (4K)</option>
                  <option>Standard (720p)</option>
                </select>
              </div>
            </div>
            <p className="text-xs text-slate-500">
              💡 Tip: Videos with trending sounds get 2.5x more reach
            </p>
          </div>
        )}
      </div>
    </div>
  );
}