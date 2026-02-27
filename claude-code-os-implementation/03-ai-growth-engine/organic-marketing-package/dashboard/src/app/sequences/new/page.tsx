"use client";

import { SequenceEditor, Sequence } from "@/components/sequences/SequenceEditor";

/**
 * New Sequence Page
 *
 * Page for creating a new email sequence from scratch or from a template.
 *
 * Features:
 * - Template selection for quick start
 * - Custom sequence builder
 * - Step management
 * - Save as draft or activate immediately
 *
 * @route /sequences/new
 */
export default function NewSequencePage() {
  /**
   * Handle sequence save
   */
  const handleSave = (sequence: Sequence) => {
    // TODO: Implement API call to save sequence
    console.log("Saving new sequence:", sequence);

    // In a real implementation, this would call:
    // await fetch('/api/sequences', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(sequence),
    // });
  };

  return <SequenceEditor onSave={handleSave} />;
}
