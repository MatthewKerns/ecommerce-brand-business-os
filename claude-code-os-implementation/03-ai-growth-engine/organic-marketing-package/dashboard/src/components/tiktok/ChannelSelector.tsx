"use client";

import { cn } from "@/lib/utils";
import { Wind, Waves, Flame, Mountain } from "lucide-react";

interface Channel {
  id: string;
  name: string;
  element: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  videoLength: string;
  audience: string;
  contentFocus: string;
}

const channels: Channel[] = [
  {
    id: "air",
    name: "Air Channel",
    element: "💨 AIR",
    description: "Quick tips, speed runs, tournament prep",
    icon: Wind,
    color: "sky",
    videoLength: "15-30 seconds",
    audience: "Competitive players, tournament grinders",
    contentFocus: "Fast-paced tips, quick wins, speed strategies",
  },
  {
    id: "water",
    name: "Water Channel",
    element: "💧 WATER",
    description: "Community stories, nostalgia, emotions",
    icon: Waves,
    color: "blue",
    videoLength: "30-60 seconds",
    audience: "Collectors, community members",
    contentFocus: "Personal stories, collection showcases, memories",
  },
  {
    id: "earth",
    name: "Earth Channel",
    element: "🪨 EARTH",
    description: "Product demos, organization tips, education",
    icon: Mountain,
    color: "emerald",
    videoLength: "30-45 seconds",
    audience: "Parents, careful buyers, quality-focused",
    contentFocus: "Product features, durability tests, tutorials",
  },
  {
    id: "fire",
    name: "Fire Channel",
    element: "🔥 FIRE",
    description: "Hot takes, debates, controversial opinions",
    icon: Flame,
    color: "orange",
    videoLength: "15-30 seconds",
    audience: "Competitive players, debate lovers",
    contentFocus: "Bold claims, controversial takes, challenges",
  },
];

interface ChannelSelectorProps {
  selectedChannel: string;
  onChannelSelect: (channel: string) => void;
}

export function ChannelSelector({
  selectedChannel,
  onChannelSelect,
}: ChannelSelectorProps) {
  const getColorClasses = (color: string, isSelected: boolean) => {
    const colorMap = {
      sky: {
        bg: isSelected ? "bg-sky-100" : "bg-white",
        border: isSelected ? "border-sky-500" : "border-slate-200",
        icon: "text-sky-600",
        badge: "bg-sky-100 text-sky-700",
      },
      blue: {
        bg: isSelected ? "bg-blue-100" : "bg-white",
        border: isSelected ? "border-blue-500" : "border-slate-200",
        icon: "text-blue-600",
        badge: "bg-blue-100 text-blue-700",
      },
      emerald: {
        bg: isSelected ? "bg-emerald-100" : "bg-white",
        border: isSelected ? "border-emerald-500" : "border-slate-200",
        icon: "text-emerald-600",
        badge: "bg-emerald-100 text-emerald-700",
      },
      orange: {
        bg: isSelected ? "bg-orange-100" : "bg-white",
        border: isSelected ? "border-orange-500" : "border-slate-200",
        icon: "text-orange-600",
        badge: "bg-orange-100 text-orange-700",
      },
    };
    return colorMap[color as keyof typeof colorMap] || colorMap.sky;
  };

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {channels.map((channel) => {
        const isSelected = selectedChannel === channel.id;
        const colorClasses = getColorClasses(channel.color, isSelected);
        const Icon = channel.icon;

        return (
          <button
            key={channel.id}
            onClick={() => onChannelSelect(channel.id)}
            className={cn(
              "group relative rounded-lg border-2 p-4 text-left transition-all hover:shadow-md",
              colorClasses.bg,
              colorClasses.border,
              isSelected ? "ring-2 ring-offset-2" : ""
            )}
          >
            {/* Channel Header */}
            <div className="mb-3 flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div
                  className={cn(
                    "rounded-lg p-2",
                    isSelected ? "bg-white/80" : "bg-slate-50"
                  )}
                >
                  <Icon className={cn("h-5 w-5", colorClasses.icon)} />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">
                    {channel.element}
                  </h3>
                  <p className="text-xs text-slate-600">{channel.videoLength}</p>
                </div>
              </div>
              {isSelected && (
                <span
                  className={cn(
                    "rounded-full px-2 py-1 text-xs font-medium",
                    colorClasses.badge
                  )}
                >
                  Selected
                </span>
              )}
            </div>

            {/* Channel Description */}
            <p className="mb-3 text-sm text-slate-700">{channel.description}</p>

            {/* Channel Details */}
            <div className="space-y-2 border-t pt-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-slate-500">
                  Audience:
                </span>
                <span className="text-xs text-slate-700">{channel.audience}</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-xs font-medium text-slate-500">Focus:</span>
                <span className="text-xs text-slate-700">
                  {channel.contentFocus}
                </span>
              </div>
            </div>

            {/* Selection Indicator */}
            {isSelected && (
              <div
                className={cn(
                  "absolute -right-1 -top-1 h-3 w-3 rounded-full",
                  channel.color === "sky" && "bg-sky-500",
                  channel.color === "blue" && "bg-blue-500",
                  channel.color === "emerald" && "bg-emerald-500",
                  channel.color === "orange" && "bg-orange-500"
                )}
              />
            )}
          </button>
        );
      })}
    </div>
  );
}