"use client";

import { useState, useEffect } from "react";
import {
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Plus,
  Clock,
  Wind,
  Waves,
  Flame,
  Mountain,
  Edit,
  Trash2,
  CheckCircle,
  AlertCircle,
  XCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ScheduledContent {
  id: string;
  channel: string;
  title: string;
  date: string;
  time: string;
  status: "scheduled" | "published" | "failed" | "draft";
  topic?: string;
  product?: string;
}

interface ContentCalendarProps {
  channel?: string;
}

// Mock data for demonstration
const mockScheduledContent: ScheduledContent[] = [
  {
    id: "1",
    channel: "air",
    title: "3-Second Deck Shuffle",
    date: "2026-02-27",
    time: "08:00",
    status: "scheduled",
    topic: "Quick shuffle technique for tournaments",
  },
  {
    id: "2",
    channel: "water",
    title: "First Tournament Story",
    date: "2026-02-27",
    time: "10:00",
    status: "scheduled",
    topic: "My journey from casual to competitive",
  },
  {
    id: "3",
    channel: "fire",
    title: "Meta Deck Hot Take",
    date: "2026-02-27",
    time: "12:00",
    status: "draft",
    topic: "Why the current meta is broken",
  },
  {
    id: "4",
    channel: "earth",
    title: "Storage System Setup",
    date: "2026-02-28",
    time: "14:00",
    status: "scheduled",
    topic: "Organizing 5000+ cards efficiently",
    product: "9-Pocket Premium Pages",
  },
  {
    id: "5",
    channel: "air",
    title: "Speed Sorting Guide",
    date: "2026-02-28",
    time: "15:00",
    status: "published",
    topic: "Sort cards in record time",
  },
];

export function ContentCalendar({ channel }: ContentCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [scheduledContent, setScheduledContent] = useState<ScheduledContent[]>(
    mockScheduledContent
  );
  const [viewMode, setViewMode] = useState<"month" | "week" | "list">("week");

  // Get channel icon
  const getChannelIcon = (channelId: string) => {
    const icons: Record<string, React.ComponentType<{ className?: string }>> = {
      air: Wind,
      water: Waves,
      fire: Flame,
      earth: Mountain,
    };
    return icons[channelId] || CalendarIcon;
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case "published":
        return "text-green-600 bg-green-100";
      case "scheduled":
        return "text-blue-600 bg-blue-100";
      case "failed":
        return "text-red-600 bg-red-100";
      case "draft":
        return "text-gray-600 bg-gray-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "published":
        return CheckCircle;
      case "scheduled":
        return Clock;
      case "failed":
        return XCircle;
      case "draft":
        return AlertCircle;
      default:
        return AlertCircle;
    }
  };

  // Filter content by channel if specified
  const filteredContent = channel
    ? scheduledContent.filter((item) => item.channel === channel)
    : scheduledContent;

  // Group content by date
  const contentByDate = filteredContent.reduce(
    (acc, item) => {
      if (!acc[item.date]) {
        acc[item.date] = [];
      }
      acc[item.date].push(item);
      return acc;
    },
    {} as Record<string, ScheduledContent[]>
  );

  // Get week dates
  const getWeekDates = () => {
    const dates = [];
    const startOfWeek = new Date(currentDate);
    startOfWeek.setDate(currentDate.getDate() - currentDate.getDay());

    for (let i = 0; i < 7; i++) {
      const date = new Date(startOfWeek);
      date.setDate(startOfWeek.getDate() + i);
      dates.push(date);
    }
    return dates;
  };

  const weekDates = getWeekDates();

  // Navigate weeks
  const goToPreviousWeek = () => {
    const newDate = new Date(currentDate);
    newDate.setDate(currentDate.getDate() - 7);
    setCurrentDate(newDate);
  };

  const goToNextWeek = () => {
    const newDate = new Date(currentDate);
    newDate.setDate(currentDate.getDate() + 7);
    setCurrentDate(newDate);
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  return (
    <div className="space-y-6">
      {/* Calendar Header */}
      <div className="rounded-lg border border-slate-200 bg-white p-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">
              Content Calendar
            </h2>
            <p className="text-sm text-slate-600">
              {channel
                ? `Showing ${channel} channel content`
                : "All channels"}
            </p>
          </div>

          <div className="flex items-center gap-2">
            {/* View Mode Selector */}
            <div className="flex rounded-lg border border-slate-200">
              <button
                onClick={() => setViewMode("week")}
                className={cn(
                  "px-3 py-1.5 text-sm",
                  viewMode === "week"
                    ? "bg-slate-900 text-white"
                    : "bg-white text-slate-600 hover:bg-slate-50"
                )}
              >
                Week
              </button>
              <button
                onClick={() => setViewMode("month")}
                className={cn(
                  "border-l border-r border-slate-200 px-3 py-1.5 text-sm",
                  viewMode === "month"
                    ? "bg-slate-900 text-white"
                    : "bg-white text-slate-600 hover:bg-slate-50"
                )}
              >
                Month
              </button>
              <button
                onClick={() => setViewMode("list")}
                className={cn(
                  "px-3 py-1.5 text-sm",
                  viewMode === "list"
                    ? "bg-slate-900 text-white"
                    : "bg-white text-slate-600 hover:bg-slate-50"
                )}
              >
                List
              </button>
            </div>

            {/* Add Content Button */}
            <button className="flex items-center gap-2 rounded-lg bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700">
              <Plus className="h-4 w-4" />
              Add Content
            </button>
          </div>
        </div>

        {/* Week Navigation */}
        {viewMode === "week" && (
          <div className="mt-4 flex items-center justify-between">
            <button
              onClick={goToPreviousWeek}
              className="rounded-lg p-1 hover:bg-slate-100"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600" />
            </button>

            <div className="flex items-center gap-2">
              <h3 className="text-sm font-medium text-slate-900">
                {weekDates[0].toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                })}
                {" - "}
                {weekDates[6].toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                })}
              </h3>
              <button
                onClick={goToToday}
                className="rounded-lg px-2 py-1 text-xs text-blue-600 hover:bg-blue-50"
              >
                Today
              </button>
            </div>

            <button
              onClick={goToNextWeek}
              className="rounded-lg p-1 hover:bg-slate-100"
            >
              <ChevronRight className="h-5 w-5 text-slate-600" />
            </button>
          </div>
        )}
      </div>

      {/* Calendar Views */}
      {viewMode === "week" && (
        <div className="rounded-lg border border-slate-200 bg-white">
          {/* Days Header */}
          <div className="grid grid-cols-7 border-b border-slate-200">
            {weekDates.map((date, index) => {
              const dateString = date.toISOString().split("T")[0];
              const isToday =
                dateString === new Date().toISOString().split("T")[0];
              const hasContent = contentByDate[dateString]?.length > 0;

              return (
                <div
                  key={index}
                  className={cn(
                    "border-r border-slate-200 p-3 text-center last:border-r-0",
                    isToday && "bg-blue-50"
                  )}
                >
                  <div className="text-xs text-slate-600">
                    {date.toLocaleDateString("en-US", { weekday: "short" })}
                  </div>
                  <div
                    className={cn(
                      "mt-1 text-lg font-semibold",
                      isToday ? "text-blue-600" : "text-slate-900"
                    )}
                  >
                    {date.getDate()}
                  </div>
                  {hasContent && (
                    <div className="mt-1 flex justify-center">
                      <div className="h-1 w-1 rounded-full bg-blue-600" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Content Grid */}
          <div className="grid min-h-[400px] grid-cols-7">
            {weekDates.map((date, dayIndex) => {
              const dateString = date.toISOString().split("T")[0];
              const dayContent = contentByDate[dateString] || [];

              return (
                <div
                  key={dayIndex}
                  className="border-r border-slate-200 p-2 last:border-r-0"
                >
                  <div className="space-y-1">
                    {dayContent.map((content) => {
                      const Icon = getChannelIcon(content.channel);
                      const StatusIcon = getStatusIcon(content.status);

                      return (
                        <div
                          key={content.id}
                          className="group cursor-pointer rounded-lg border border-slate-200 p-2 hover:border-slate-300 hover:shadow-sm"
                        >
                          {/* Content Header */}
                          <div className="flex items-center justify-between">
                            <Icon className="h-3 w-3 text-slate-600" />
                            <span className="text-xs text-slate-500">
                              {content.time}
                            </span>
                          </div>

                          {/* Content Title */}
                          <p className="mt-1 line-clamp-2 text-xs font-medium text-slate-900">
                            {content.title}
                          </p>

                          {/* Status Badge */}
                          <div className="mt-1 flex items-center gap-1">
                            <StatusIcon
                              className={cn(
                                "h-3 w-3",
                                content.status === "published" &&
                                  "text-green-600",
                                content.status === "scheduled" &&
                                  "text-blue-600",
                                content.status === "failed" && "text-red-600",
                                content.status === "draft" && "text-gray-600"
                              )}
                            />
                            <span
                              className={cn(
                                "rounded-full px-1.5 py-0.5 text-xs",
                                getStatusColor(content.status)
                              )}
                            >
                              {content.status}
                            </span>
                          </div>

                          {/* Hover Actions */}
                          <div className="mt-1 hidden justify-end gap-1 group-hover:flex">
                            <button className="rounded p-0.5 hover:bg-slate-100">
                              <Edit className="h-3 w-3 text-slate-600" />
                            </button>
                            <button className="rounded p-0.5 hover:bg-slate-100">
                              <Trash2 className="h-3 w-3 text-red-600" />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* List View */}
      {viewMode === "list" && (
        <div className="rounded-lg border border-slate-200 bg-white">
          <div className="max-h-[600px] overflow-y-auto">
            <table className="w-full">
              <thead className="sticky top-0 bg-slate-50">
                <tr className="border-b border-slate-200 text-left">
                  <th className="p-3 text-sm font-medium text-slate-700">
                    Channel
                  </th>
                  <th className="p-3 text-sm font-medium text-slate-700">
                    Title
                  </th>
                  <th className="p-3 text-sm font-medium text-slate-700">
                    Date & Time
                  </th>
                  <th className="p-3 text-sm font-medium text-slate-700">
                    Status
                  </th>
                  <th className="p-3 text-sm font-medium text-slate-700">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredContent.map((content) => {
                  const Icon = getChannelIcon(content.channel);
                  const StatusIcon = getStatusIcon(content.status);

                  return (
                    <tr
                      key={content.id}
                      className="border-b border-slate-200 hover:bg-slate-50"
                    >
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          <Icon className="h-4 w-4 text-slate-600" />
                          <span className="text-sm capitalize text-slate-900">
                            {content.channel}
                          </span>
                        </div>
                      </td>
                      <td className="p-3">
                        <div>
                          <p className="text-sm font-medium text-slate-900">
                            {content.title}
                          </p>
                          {content.topic && (
                            <p className="text-xs text-slate-600">
                              {content.topic}
                            </p>
                          )}
                        </div>
                      </td>
                      <td className="p-3">
                        <div className="text-sm text-slate-700">
                          {new Date(content.date).toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                          })}
                          {" at "}
                          {content.time}
                        </div>
                      </td>
                      <td className="p-3">
                        <div className="flex items-center gap-1">
                          <StatusIcon
                            className={cn(
                              "h-4 w-4",
                              content.status === "published" &&
                                "text-green-600",
                              content.status === "scheduled" &&
                                "text-blue-600",
                              content.status === "failed" && "text-red-600",
                              content.status === "draft" && "text-gray-600"
                            )}
                          />
                          <span
                            className={cn(
                              "rounded-full px-2 py-1 text-xs",
                              getStatusColor(content.status)
                            )}
                          >
                            {content.status}
                          </span>
                        </div>
                      </td>
                      <td className="p-3">
                        <div className="flex gap-2">
                          <button className="rounded p-1 hover:bg-slate-100">
                            <Edit className="h-4 w-4 text-slate-600" />
                          </button>
                          <button className="rounded p-1 hover:bg-slate-100">
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Stats Summary */}
      <div className="grid gap-4 sm:grid-cols-4">
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="text-2xl font-bold text-slate-900">
            {filteredContent.filter((c) => c.status === "scheduled").length}
          </p>
          <p className="text-sm text-slate-600">Scheduled</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="text-2xl font-bold text-green-600">
            {filteredContent.filter((c) => c.status === "published").length}
          </p>
          <p className="text-sm text-slate-600">Published</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="text-2xl font-bold text-gray-600">
            {filteredContent.filter((c) => c.status === "draft").length}
          </p>
          <p className="text-sm text-slate-600">Drafts</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="text-2xl font-bold text-red-600">
            {filteredContent.filter((c) => c.status === "failed").length}
          </p>
          <p className="text-sm text-slate-600">Failed</p>
        </div>
      </div>
    </div>
  );
}