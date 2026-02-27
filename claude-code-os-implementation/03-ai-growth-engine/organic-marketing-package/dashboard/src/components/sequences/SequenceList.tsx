"use client";

import {
  Play,
  Pause,
  FileText,
  Mail,
  MousePointer,
  TrendingUp,
  MoreVertical,
  Copy,
  Edit2,
  Trash2,
} from "lucide-react";
import { useState } from "react";

/**
 * Email sequence data type
 */
export interface EmailSequence {
  /** Unique identifier */
  id: string;
  /** Sequence name */
  name: string;
  /** Sequence description */
  description: string;
  /** Status: active, paused, or draft */
  status: "active" | "paused" | "draft";
  /** Number of emails in sequence */
  emailCount: number;
  /** Total subscribers enrolled */
  subscribersEnrolled: number;
  /** Emails sent */
  emailsSent: number;
  /** Open rate percentage */
  openRate: number;
  /** Click rate percentage */
  clickRate: number;
  /** Conversion rate percentage */
  conversionRate: number;
  /** Last updated timestamp */
  lastUpdated: string;
}

/**
 * Mock sequence data for demonstration
 */
const MOCK_SEQUENCES: EmailSequence[] = [
  {
    id: "seq-1",
    name: "Welcome Series",
    description: "4-email welcome sequence for new subscribers",
    status: "active",
    emailCount: 4,
    subscribersEnrolled: 1247,
    emailsSent: 4988,
    openRate: 42.5,
    clickRate: 12.3,
    conversionRate: 3.8,
    lastUpdated: "2024-02-26T10:30:00Z",
  },
  {
    id: "seq-2",
    name: "Nurture Campaign",
    description: "Educational content for non-buyers over 5 weeks",
    status: "active",
    emailCount: 4,
    subscribersEnrolled: 892,
    emailsSent: 3568,
    openRate: 38.2,
    clickRate: 9.7,
    conversionRate: 2.1,
    lastUpdated: "2024-02-25T14:15:00Z",
  },
  {
    id: "seq-3",
    name: "Product Launch Sequence",
    description: "Pre-launch hype and post-launch follow-up",
    status: "paused",
    emailCount: 6,
    subscribersEnrolled: 543,
    emailsSent: 2172,
    openRate: 51.3,
    clickRate: 18.9,
    conversionRate: 7.2,
    lastUpdated: "2024-02-20T08:45:00Z",
  },
  {
    id: "seq-4",
    name: "Re-engagement Series",
    description: "Win back inactive subscribers",
    status: "draft",
    emailCount: 3,
    subscribersEnrolled: 0,
    emailsSent: 0,
    openRate: 0,
    clickRate: 0,
    conversionRate: 0,
    lastUpdated: "2024-02-26T16:20:00Z",
  },
];

/**
 * Format date to relative time
 */
function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 60) {
    return `${diffMins}m ago`;
  }
  if (diffHours < 24) {
    return `${diffHours}h ago`;
  }
  if (diffDays < 7) {
    return `${diffDays}d ago`;
  }
  return date.toLocaleDateString();
}

/**
 * SequenceList Component
 *
 * Displays a table of email sequences with key metrics and actions.
 *
 * Features:
 * - Status badges (active, paused, draft)
 * - Key metrics displayed inline (sent, open rate, click rate, conversion)
 * - Action menu for each sequence (edit, duplicate, delete)
 * - Responsive layout
 * - Empty state when no sequences exist
 *
 * @example
 * ```tsx
 * <SequenceList />
 * ```
 */
export function SequenceList() {
  const [sequences] = useState<EmailSequence[]>(MOCK_SEQUENCES);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);

  /**
   * Get status badge styling
   */
  const getStatusBadge = (status: EmailSequence["status"]) => {
    const styles = {
      active: "bg-green-100 text-green-800",
      paused: "bg-yellow-100 text-yellow-800",
      draft: "bg-slate-100 text-slate-600",
    };

    const labels = {
      active: "Active",
      paused: "Paused",
      draft: "Draft",
    };

    return (
      <span
        className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[status]}`}
      >
        {status === "active" && <Play className="h-3 w-3" />}
        {status === "paused" && <Pause className="h-3 w-3" />}
        {status === "draft" && <FileText className="h-3 w-3" />}
        {labels[status]}
      </span>
    );
  };

  /**
   * Toggle action menu for sequence
   */
  const toggleMenu = (sequenceId: string) => {
    setActiveMenu(activeMenu === sequenceId ? null : sequenceId);
  };

  // Empty state
  if (sequences.length === 0) {
    return (
      <div className="rounded-lg border-2 border-dashed border-slate-200 bg-slate-50 p-12 text-center">
        <Mail className="mx-auto h-12 w-12 text-slate-400" />
        <h3 className="mt-4 text-lg font-semibold text-slate-900">
          No sequences yet
        </h3>
        <p className="mt-2 text-sm text-slate-600">
          Create your first email sequence to start engaging subscribers
        </p>
        <button className="mt-6 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-800">
          Create Your First Sequence
        </button>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
      {/* Desktop Table View */}
      <div className="hidden overflow-x-auto md:block">
        <table className="w-full">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-600">
                Sequence
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-600">
                Status
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-600">
                Subscribers
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-600">
                Sent
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-600">
                Open Rate
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-600">
                Click Rate
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-600">
                Conversion
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-600">
                Updated
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-600">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {sequences.map((sequence) => (
              <tr
                key={sequence.id}
                className="transition-colors hover:bg-slate-50"
              >
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100">
                      <Mail className="h-5 w-5 text-slate-600" />
                    </div>
                    <div>
                      <div className="font-medium text-slate-900">
                        {sequence.name}
                      </div>
                      <div className="text-sm text-slate-600">
                        {sequence.emailCount} emails
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  {getStatusBadge(sequence.status)}
                </td>
                <td className="px-6 py-4 text-right text-sm text-slate-900">
                  {sequence.subscribersEnrolled.toLocaleString()}
                </td>
                <td className="px-6 py-4 text-right text-sm text-slate-900">
                  {sequence.emailsSent.toLocaleString()}
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end gap-1.5">
                    <Mail className="h-4 w-4 text-slate-400" />
                    <span className="text-sm font-medium text-slate-900">
                      {sequence.openRate.toFixed(1)}%
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end gap-1.5">
                    <MousePointer className="h-4 w-4 text-slate-400" />
                    <span className="text-sm font-medium text-slate-900">
                      {sequence.clickRate.toFixed(1)}%
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end gap-1.5">
                    <TrendingUp className="h-4 w-4 text-slate-400" />
                    <span className="text-sm font-medium text-slate-900">
                      {sequence.conversionRate.toFixed(1)}%
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 text-right text-sm text-slate-600">
                  {formatRelativeTime(sequence.lastUpdated)}
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="relative">
                    <button
                      onClick={() => toggleMenu(sequence.id)}
                      className="rounded-md p-1 text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900"
                    >
                      <MoreVertical className="h-5 w-5" />
                    </button>
                    {activeMenu === sequence.id && (
                      <div className="absolute right-0 z-10 mt-2 w-48 rounded-md border border-slate-200 bg-white shadow-lg">
                        <div className="py-1">
                          <button className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm text-slate-700 transition-colors hover:bg-slate-50">
                            <Edit2 className="h-4 w-4" />
                            Edit
                          </button>
                          <button className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm text-slate-700 transition-colors hover:bg-slate-50">
                            <Copy className="h-4 w-4" />
                            Duplicate
                          </button>
                          <button className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm text-red-600 transition-colors hover:bg-red-50">
                            <Trash2 className="h-4 w-4" />
                            Delete
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Card View */}
      <div className="divide-y divide-slate-200 md:hidden">
        {sequences.map((sequence) => (
          <div key={sequence.id} className="p-4">
            <div className="mb-3 flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100">
                  <Mail className="h-5 w-5 text-slate-600" />
                </div>
                <div>
                  <div className="font-medium text-slate-900">
                    {sequence.name}
                  </div>
                  <div className="text-sm text-slate-600">
                    {sequence.emailCount} emails
                  </div>
                </div>
              </div>
              {getStatusBadge(sequence.status)}
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <div className="text-slate-600">Subscribers</div>
                <div className="font-medium text-slate-900">
                  {sequence.subscribersEnrolled.toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-slate-600">Sent</div>
                <div className="font-medium text-slate-900">
                  {sequence.emailsSent.toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-slate-600">Open Rate</div>
                <div className="font-medium text-slate-900">
                  {sequence.openRate.toFixed(1)}%
                </div>
              </div>
              <div>
                <div className="text-slate-600">Click Rate</div>
                <div className="font-medium text-slate-900">
                  {sequence.clickRate.toFixed(1)}%
                </div>
              </div>
            </div>

            <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-3">
              <span className="text-xs text-slate-600">
                Updated {formatRelativeTime(sequence.lastUpdated)}
              </span>
              <button
                onClick={() => toggleMenu(sequence.id)}
                className="rounded-md p-1 text-slate-600 transition-colors hover:bg-slate-100"
              >
                <MoreVertical className="h-5 w-5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
