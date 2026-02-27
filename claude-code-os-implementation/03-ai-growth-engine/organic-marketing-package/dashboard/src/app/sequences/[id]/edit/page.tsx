"use client";

import { use } from "react";
import { SequenceEditor, Sequence } from "@/components/sequences/SequenceEditor";
import { SequenceStep } from "@/components/sequences/StepBuilder";

/**
 * Mock sequence data for demonstration
 * In a real implementation, this would be fetched from an API
 */
const MOCK_SEQUENCES: Record<string, Sequence> = {
  "seq-1": {
    id: "seq-1",
    name: "Welcome Series",
    description: "4-email welcome sequence for new subscribers",
    status: "active",
    templateId: "welcome-series",
    steps: [
      {
        id: "step-1",
        name: "Welcome Email",
        subject: "Welcome! Here's what to expect 👋",
        previewText: "We're excited to have you here",
        delayDays: 0,
        sendAtHour: 10,
        status: "active",
      },
      {
        id: "step-2",
        name: "Brand Story",
        subject: "The story behind our brand",
        previewText: "Learn about our journey and mission",
        delayDays: 2,
        sendAtHour: 10,
        status: "active",
      },
      {
        id: "step-3",
        name: "Social Proof",
        subject: "Real results from real customers",
        previewText: "See what others are saying",
        delayDays: 3,
        sendAtHour: 10,
        status: "active",
      },
      {
        id: "step-4",
        name: "First Purchase Offer",
        subject: "Your exclusive first-time offer",
        previewText: "Special discount just for you",
        delayDays: 2,
        sendAtHour: 10,
        status: "active",
      },
    ],
  },
  "seq-2": {
    id: "seq-2",
    name: "Nurture Campaign",
    description: "Educational content for non-buyers over 5 weeks",
    status: "active",
    templateId: "nurture-series",
    steps: [
      {
        id: "step-1",
        name: "Educational Foundation",
        subject: "The ultimate guide to [topic]",
        previewText: "Everything you need to know",
        delayDays: 0,
        sendAtHour: 10,
        status: "active",
      },
      {
        id: "step-2",
        name: "Success Stories",
        subject: "How [customer] achieved [result]",
        previewText: "Real case study",
        delayDays: 7,
        sendAtHour: 10,
        status: "active",
      },
      {
        id: "step-3",
        name: "Exclusive Insights",
        subject: "Insider tips you won't find anywhere else",
        previewText: "Advanced strategies revealed",
        delayDays: 7,
        sendAtHour: 10,
        status: "active",
      },
      {
        id: "step-4",
        name: "Conversion Offer",
        subject: "Last chance: Special offer inside",
        previewText: "Don't miss out",
        delayDays: 14,
        sendAtHour: 10,
        status: "active",
      },
    ],
  },
};

/**
 * Edit Sequence Page
 *
 * Page for editing an existing email sequence.
 *
 * Features:
 * - Load existing sequence data
 * - Edit sequence metadata and steps
 * - Update and save changes
 * - Activate/deactivate sequence
 *
 * @route /sequences/[id]/edit
 */
export default function EditSequencePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  // Unwrap params using React.use()
  const { id } = use(params);

  // Fetch sequence data (using mock data for now)
  const sequence = MOCK_SEQUENCES[id];

  /**
   * Handle sequence save
   */
  const handleSave = (updatedSequence: Sequence) => {
    // TODO: Implement API call to update sequence
    console.log("Updating sequence:", updatedSequence);

    // In a real implementation, this would call:
    // await fetch(`/api/sequences/${id}`, {
    //   method: 'PUT',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(updatedSequence),
    // });
  };

  // Show error if sequence not found
  if (!sequence) {
    return (
      <div className="space-y-8">
        <div className="rounded-lg border border-red-200 bg-red-50 p-6">
          <h2 className="mb-2 text-lg font-semibold text-red-900">
            Sequence Not Found
          </h2>
          <p className="text-sm text-red-700">
            The sequence with ID &quot;{id}&quot; could not be found.
          </p>
        </div>
      </div>
    );
  }

  return <SequenceEditor sequence={sequence} onSave={handleSave} />;
}
