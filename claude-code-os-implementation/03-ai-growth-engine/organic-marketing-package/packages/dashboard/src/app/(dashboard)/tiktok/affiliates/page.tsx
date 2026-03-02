"use client";

import React from "react";
import { CampaignControls } from "@/components/affiliates/CampaignControls";
import { DraftReview } from "@/components/affiliates/DraftReview";
import { StyleChat } from "@/components/affiliates/StyleChat";

export default function AffiliateOutreachPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b pb-4">
        <h1 className="text-2xl font-bold text-slate-900">
          Affiliate Outreach
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Manage automations, review draft messages, tune your style
        </p>
      </div>

      {/* Main layout: left column = drafts, right column = controls + chat */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left: Draft review (takes 2/3 on large screens) */}
        <div className="lg:col-span-2">
          <DraftReview />
        </div>

        {/* Right: Controls + Style Chat */}
        <div className="space-y-6">
          <CampaignControls />
          <StyleChat />
        </div>
      </div>
    </div>
  );
}
