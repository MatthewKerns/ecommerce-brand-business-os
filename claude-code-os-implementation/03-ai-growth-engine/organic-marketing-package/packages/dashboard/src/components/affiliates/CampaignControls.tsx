"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Play,
  Pause,
  RefreshCw,
  Loader2,
  Users,
  TrendingUp,
  Send,
  Clock,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface TierProgress {
  current_tier: number;
  next_tier: number | null;
  requirement: string;
  affiliate_gmv_30d: number;
  progress_percent: number;
  weekly_limit: number;
  actions_remaining: number;
  max_follower_limit: number | null;
}

interface CampaignReport {
  campaign_name: string;
  status: string;
  total_invitations_sent: number;
  accepted: number;
  rejected: number;
  pending: number;
  acceptance_rate: number;
}

export function CampaignControls() {
  const [tierProgress, setTierProgress] = useState<TierProgress | null>(null);
  const [campaigns, setCampaigns] = useState<CampaignReport[]>([]);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState<string | null>(null);

  const loadStatus = async () => {
    setLoading(true);
    try {
      const tier = await apiClient.get<TierProgress>(
        `${API_BASE}/tiktok/affiliates/tier-progress`
      );
      setTierProgress(tier);
    } catch {
      // Use placeholder data when API isn't connected
      setTierProgress({
        current_tier: 1,
        next_tier: 2,
        requirement: "Make 1 affiliate sale ($1 minimum)",
        affiliate_gmv_30d: 0,
        progress_percent: 0,
        weekly_limit: 1000,
        actions_remaining: 1000,
        max_follower_limit: null,
      });
    }
    setLoading(false);
  };

  const executeDailyOutreach = async (campaignName: string) => {
    setExecuting(campaignName);
    try {
      await apiClient.post(
        `${API_BASE}/tiktok/affiliates/campaigns/${encodeURIComponent(campaignName)}/execute`,
        {}
      );
    } catch {
      // noop - will show in campaign report
    }
    setExecuting(null);
  };

  const executeFollowUps = async (campaignName: string) => {
    setExecuting(campaignName + "_followup");
    try {
      await apiClient.post(
        `${API_BASE}/tiktok/affiliates/campaigns/${encodeURIComponent(campaignName)}/follow-up`,
        {}
      );
    } catch {
      // noop
    }
    setExecuting(null);
  };

  React.useEffect(() => {
    loadStatus();
  }, []);

  const tierColors: Record<number, string> = {
    1: "bg-gray-100 text-gray-800",
    2: "bg-blue-100 text-blue-800",
    3: "bg-green-100 text-green-800",
  };

  return (
    <div className="space-y-4">
      {/* Tier Progress */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Outreach Tier</CardTitle>
            <Button variant="ghost" size="icon" onClick={loadStatus} disabled={loading}>
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {tierProgress ? (
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <Badge className={tierColors[tierProgress.current_tier] || ""}>
                  Tier {tierProgress.current_tier}
                </Badge>
                <span className="text-sm text-slate-600">
                  {tierProgress.actions_remaining}/{tierProgress.weekly_limit} actions left this week
                </span>
              </div>

              {tierProgress.next_tier && (
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Progress to Tier {tierProgress.next_tier}</span>
                    <span className="font-medium">{tierProgress.progress_percent}%</span>
                  </div>
                  <Progress value={tierProgress.progress_percent} />
                  <p className="text-xs text-slate-500">{tierProgress.requirement}</p>
                  {tierProgress.current_tier === 2 && (
                    <p className="text-xs font-medium text-slate-700">
                      ${tierProgress.affiliate_gmv_30d.toFixed(0)} / $2,000 GMV
                    </p>
                  )}
                </div>
              )}

              {tierProgress.max_follower_limit && (
                <p className="text-xs text-amber-600">
                  Limited to creators with &lt;{(tierProgress.max_follower_limit / 1000).toFixed(0)}K followers
                </p>
              )}

              {/* Quick Stats */}
              <div className="grid grid-cols-3 gap-2 pt-2 border-t">
                <div className="text-center">
                  <p className="text-lg font-semibold text-slate-900">
                    {tierProgress.weekly_limit}
                  </p>
                  <p className="text-xs text-slate-500">Weekly Limit</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-semibold text-slate-900">
                    {tierProgress.weekly_limit - tierProgress.actions_remaining}
                  </p>
                  <p className="text-xs text-slate-500">Used</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-semibold text-blue-600">
                    ${tierProgress.affiliate_gmv_30d.toFixed(0)}
                  </p>
                  <p className="text-xs text-slate-500">GMV 30d</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-20">
              <Loader2 className="h-5 w-5 animate-spin text-slate-400" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Campaign Controls */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Automation Controls</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-slate-600">
            Run daily outreach or follow-ups for active campaigns.
          </p>

          {campaigns.length === 0 && (
            <div className="text-center py-4 text-sm text-slate-500">
              <Users className="h-8 w-8 mx-auto mb-2 text-slate-300" />
              <p>No campaigns yet.</p>
              <p className="text-xs">Create one via the API to get started.</p>
            </div>
          )}

          {campaigns.map((campaign) => (
            <div
              key={campaign.campaign_name}
              className="rounded-md border p-3 space-y-2"
            >
              <div className="flex items-center justify-between">
                <span className="font-medium text-sm">{campaign.campaign_name}</span>
                <Badge variant={campaign.status === "active" ? "default" : "secondary"}>
                  {campaign.status}
                </Badge>
              </div>

              <div className="flex gap-4 text-xs text-slate-600">
                <span className="flex items-center gap-1">
                  <Send className="h-3 w-3" /> {campaign.total_invitations_sent} sent
                </span>
                <span className="flex items-center gap-1">
                  <TrendingUp className="h-3 w-3" /> {campaign.acceptance_rate}% accepted
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" /> {campaign.pending} pending
                </span>
              </div>

              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={() => executeDailyOutreach(campaign.campaign_name)}
                  disabled={executing !== null}
                >
                  {executing === campaign.campaign_name ? (
                    <Loader2 className="h-3 w-3 animate-spin mr-1" />
                  ) : (
                    <Play className="h-3 w-3 mr-1" />
                  )}
                  Run Outreach
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => executeFollowUps(campaign.campaign_name)}
                  disabled={executing !== null}
                >
                  {executing === campaign.campaign_name + "_followup" ? (
                    <Loader2 className="h-3 w-3 animate-spin mr-1" />
                  ) : (
                    <RefreshCw className="h-3 w-3 mr-1" />
                  )}
                  Follow-ups
                </Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
