"use client";

import React, { useState, Suspense, useEffect } from "react";
import dynamic from "next/dynamic";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Video, Calendar, BarChart3, Sparkles, Loader2, AlertCircle } from "lucide-react";
import { TikTokErrorBoundary } from "@/components/error-boundaries";

// Fallback component for when ChannelSelector fails to load
function ChannelSelectorFallback({ error }: { error?: Error }) {
  const mockChannels = [
    { id: "air", name: "Air Channel", element: "💨 AIR", color: "bg-sky-100 border-sky-300" },
    { id: "water", name: "Water Channel", element: "💧 WATER", color: "bg-blue-100 border-blue-300" },
    { id: "earth", name: "Earth Channel", element: "🪨 EARTH", color: "bg-emerald-100 border-emerald-300" },
    { id: "fire", name: "Fire Channel", element: "🔥 FIRE", color: "bg-orange-100 border-orange-300" },
  ];

  return (
    <div className="space-y-4">
      {error && (
        <div className="rounded-md bg-yellow-50 border border-yellow-200 p-3">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-yellow-600 mr-2 flex-shrink-0" />
            <div className="text-sm text-yellow-700">
              <p className="font-medium">Channel selector loading issue</p>
              <p className="mt-1">Using fallback interface. Functionality may be limited.</p>
            </div>
          </div>
        </div>
      )}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {mockChannels.map((channel) => (
          <button
            key={channel.id}
            className={`relative rounded-lg border-2 p-4 text-center transition-all hover:shadow-lg ${channel.color}`}
            onClick={() => console.log(`Selected channel: ${channel.id}`)}
          >
            <div className="mb-2 text-2xl">{channel.element}</div>
            <p className="text-sm font-medium text-gray-700">{channel.name}</p>
          </button>
        ))}
      </div>
    </div>
  );
}

// Loading component
function ComponentLoader() {
  return (
    <div className="h-64 flex items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
    </div>
  );
}

// Fix dynamic imports with proper error handling
const ChannelSelector = dynamic(
  () => import("@/components/tiktok/ChannelSelector")
    .then((mod) => {
      // Check if the module and export exist
      if (mod && mod.ChannelSelector) {
        return { default: mod.ChannelSelector };
      }
      // If not, return the fallback
      console.warn("ChannelSelector export not found, using fallback");
      return { default: ChannelSelectorFallback };
    })
    .catch((error) => {
      console.error("Failed to load ChannelSelector:", error);
      // Return fallback on error
      return {
        default: (props: any) => <ChannelSelectorFallback error={error} {...props} />
      };
    }),
  {
    ssr: false,
    loading: () => <ComponentLoader />
  }
);

const ScriptGeneratorForm = dynamic(
  () => import("@/components/tiktok/ScriptGeneratorForm")
    .then((mod) => {
      if (mod && mod.ScriptGeneratorForm) {
        return { default: mod.ScriptGeneratorForm };
      }
      // Fallback component
      return {
        default: () => (
          <div className="p-6 text-center text-gray-500">
            <Video className="h-12 w-12 mx-auto mb-2 text-gray-400" />
            <p>Script Generator is temporarily unavailable</p>
            <p className="text-sm mt-2">Please check your connection and try again</p>
          </div>
        )
      };
    })
    .catch(() => ({
      default: () => (
        <div className="p-6 text-center text-gray-500">
          <Video className="h-12 w-12 mx-auto mb-2 text-gray-400" />
          <p>Script Generator could not be loaded</p>
        </div>
      )
    })),
  {
    ssr: false,
    loading: () => <ComponentLoader />
  }
);

const GeneratedScriptDisplay = dynamic(
  () => import("@/components/tiktok/GeneratedScriptDisplay")
    .then((mod) => {
      if (mod && mod.GeneratedScriptDisplay) {
        return { default: mod.GeneratedScriptDisplay };
      }
      return {
        default: () => (
          <div className="p-6 text-center text-gray-500">
            <p>Script display unavailable</p>
          </div>
        )
      };
    })
    .catch(() => ({
      default: () => (
        <div className="p-6 text-center text-gray-500">
          <p>Script display could not be loaded</p>
        </div>
      )
    })),
  {
    ssr: false,
    loading: () => <ComponentLoader />
  }
);

const VideoGenerator = dynamic(
  () => import("@/components/tiktok/VideoGenerator")
    .then((mod) => {
      if (mod && mod.VideoGenerator) {
        return { default: mod.VideoGenerator };
      }
      return {
        default: () => (
          <div className="p-6 text-center text-gray-500">
            <Video className="h-12 w-12 mx-auto mb-2 text-gray-400" />
            <p>Video Generator unavailable</p>
          </div>
        )
      };
    })
    .catch(() => ({
      default: () => (
        <div className="p-6 text-center text-gray-500">
          <Video className="h-12 w-12 mx-auto mb-2 text-gray-400" />
          <p>Video Generator could not be loaded</p>
        </div>
      )
    })),
  {
    ssr: false,
    loading: () => <ComponentLoader />
  }
);

const ContentCalendar = dynamic(
  () => import("@/components/tiktok/ContentCalendar")
    .then((mod) => {
      if (mod && mod.ContentCalendar) {
        return { default: mod.ContentCalendar };
      }
      return {
        default: () => (
          <div className="rounded-lg border border-slate-200 bg-white p-8 text-center">
            <Calendar className="mx-auto h-12 w-12 text-slate-400" />
            <h3 className="mt-4 text-lg font-semibold text-slate-900">
              Content Calendar
            </h3>
            <p className="mt-2 text-sm text-slate-600">
              Calendar component is currently unavailable
            </p>
          </div>
        )
      };
    })
    .catch(() => ({
      default: () => (
        <div className="rounded-lg border border-slate-200 bg-white p-8 text-center">
          <Calendar className="mx-auto h-12 w-12 text-slate-400" />
          <p className="text-sm text-slate-600">Calendar could not be loaded</p>
        </div>
      )
    })),
  {
    ssr: false,
    loading: () => <ComponentLoader />
  }
);

function TikTokContentStudioContent() {
  const [selectedChannel, setSelectedChannel] = useState<string>("air");
  const [generatedScript, setGeneratedScript] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Debug logging
  useEffect(() => {
    console.log("TikTok Studio - Generated Script:", generatedScript);
    console.log("TikTok Studio - Selected Channel:", selectedChannel);
  }, [generatedScript, selectedChannel]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b pb-6">
        <h1 className="text-3xl font-bold text-slate-900">
          TikTok Content Studio
        </h1>
        <p className="mt-2 text-slate-600">
          Create viral TikTok content with our 4-channel element strategy
        </p>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="create" className="space-y-6">
        <TabsList className="grid w-full max-w-md grid-cols-4">
          <TabsTrigger value="create" className="flex items-center gap-2">
            <Video className="h-4 w-4" />
            Create
          </TabsTrigger>
          <TabsTrigger value="calendar" className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Calendar
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Analytics
          </TabsTrigger>
          <TabsTrigger value="campaigns" className="flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            Campaigns
          </TabsTrigger>
        </TabsList>

        {/* Create Tab */}
        <TabsContent value="create" className="space-y-6">
          {/* Channel Selection */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <h2 className="mb-4 text-xl font-semibold">Select Channel</h2>
            <ChannelSelector
              selectedChannel={selectedChannel}
              onChannelSelect={setSelectedChannel}
            />
          </div>

          {/* Script Generator */}
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-lg border border-slate-200 bg-white p-6">
              <h2 className="mb-4 text-xl font-semibold">Generate Script</h2>
              <ScriptGeneratorForm
                channel={selectedChannel}
                onScriptGenerated={setGeneratedScript}
                isGenerating={isGenerating}
                setIsGenerating={setIsGenerating}
              />
            </div>

            {/* Generated Script Display */}
            <div className="rounded-lg border border-slate-200 bg-white p-6">
              <h2 className="mb-4 text-xl font-semibold">Generated Script</h2>
              <GeneratedScriptDisplay
                script={generatedScript}
                isLoading={isGenerating}
                channel={selectedChannel}
              />
            </div>
          </div>

          {/* Video Generator */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <VideoGenerator
              script={generatedScript}
              channel={selectedChannel}
            />
          </div>
        </TabsContent>

        {/* Calendar Tab */}
        <TabsContent value="calendar" className="space-y-6">
          <ContentCalendar channel={selectedChannel} />
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics">
          <div className="rounded-lg border border-slate-200 bg-white p-8 text-center">
            <BarChart3 className="mx-auto h-12 w-12 text-slate-400" />
            <h3 className="mt-4 text-lg font-semibold text-slate-900">
              Channel Analytics
            </h3>
            <p className="mt-2 text-sm text-slate-600">
              Performance metrics for your TikTok channels coming soon
            </p>
          </div>
        </TabsContent>

        {/* Campaigns Tab */}
        <TabsContent value="campaigns">
          <div className="rounded-lg border border-slate-200 bg-white p-8 text-center">
            <Sparkles className="mx-auto h-12 w-12 text-slate-400" />
            <h3 className="mt-4 text-lg font-semibold text-slate-900">
              Multi-Channel Campaigns
            </h3>
            <p className="mt-2 text-sm text-slate-600">
              Coordinate campaigns across all 4 channels coming soon
            </p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function TikTokContentStudio() {
  return (
    <TikTokErrorBoundary>
      <Suspense fallback={
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
            <p className="mt-4 text-sm text-slate-600">Loading TikTok Studio...</p>
          </div>
        </div>
      }>
        <TikTokContentStudioContent />
      </Suspense>
    </TikTokErrorBoundary>
  );
}