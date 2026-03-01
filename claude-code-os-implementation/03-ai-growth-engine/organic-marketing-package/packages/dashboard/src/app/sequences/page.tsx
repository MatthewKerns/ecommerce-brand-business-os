"use client";

import { Mail } from "lucide-react";
import Link from "next/link";
import { SequenceList } from "@/components/sequences/SequenceList";

/**
 * Sequences Page
 *
 * Main page for viewing and managing email sequences.
 *
 * Features:
 * - List view of all email sequences with metrics
 * - Quick stats for each sequence (sent, opened, clicked, converted)
 * - Create new sequence button
 * - Edit/duplicate/delete actions
 * - Status indicators (active, paused, draft)
 *
 * @route /sequences
 */
export default function SequencesPage() {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-slate-100 p-3">
            <Mail className="h-6 w-6 text-slate-700" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">
              Email Sequences
            </h1>
            <p className="text-sm text-slate-600">
              Automated welcome and nurture email campaigns
            </p>
          </div>
        </div>

        {/* Create New Sequence Button */}
        <Link
          href="/sequences/new"
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-800"
        >
          Create Sequence
        </Link>
      </div>

      {/* Sequence List */}
      <SequenceList />
    </div>
  );
}
