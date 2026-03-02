"use client";

import React, { useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Send,
  Check,
  X,
  RefreshCw,
  Loader2,
  CheckSquare,
  Square,
  Edit3,
  Users,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface Draft {
  draft_id: string;
  creator_id: string;
  creator_nickname: string;
  creator_followers: number | null;
  creator_gmv_30d: number | null;
  campaign_name: string;
  context: string;
  days_pending: number;
  draft_message: string;
  status: string;
  generated_at: string;
}

export function DraftReview() {
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [generating, setGenerating] = useState(false);

  const generateDrafts = async () => {
    setGenerating(true);
    try {
      const result = await apiClient.post<{ drafts: Draft[] }>(
        `${API_BASE}/tiktok/affiliates/drafts/generate`,
        {}
      );
      setDrafts(result.drafts);
      setSelected(new Set());
    } catch {
      // Demo data for when API isn't connected
      setDrafts([]);
    }
    setGenerating(false);
  };

  const loadDrafts = async () => {
    setLoading(true);
    try {
      const result = await apiClient.get<{ drafts: Draft[] }>(
        `${API_BASE}/tiktok/affiliates/drafts?status=pending`
      );
      setDrafts(result.drafts);
    } catch {
      setDrafts([]);
    }
    setLoading(false);
  };

  const toggleSelect = (draftId: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(draftId)) {
        next.delete(draftId);
      } else {
        next.add(draftId);
      }
      return next;
    });
  };

  const selectAll = () => {
    if (selected.size === drafts.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(drafts.map((d) => d.draft_id)));
    }
  };

  const startEdit = (draft: Draft) => {
    setEditingId(draft.draft_id);
    setEditText(draft.draft_message);
  };

  const saveEdit = async () => {
    if (!editingId) return;
    try {
      await apiClient.put(
        `${API_BASE}/tiktok/affiliates/drafts/${editingId}`,
        { draft_id: editingId, message: editText }
      );
      setDrafts((prev) =>
        prev.map((d) =>
          d.draft_id === editingId ? { ...d, draft_message: editText } : d
        )
      );
    } catch {
      // noop
    }
    setEditingId(null);
    setEditText("");
  };

  const batchSend = async () => {
    if (selected.size === 0) return;
    setSending(true);
    try {
      await apiClient.post(`${API_BASE}/tiktok/affiliates/drafts/batch-send`, {
        draft_ids: Array.from(selected),
      });
      // Remove sent drafts from list
      setDrafts((prev) => prev.filter((d) => !selected.has(d.draft_id)));
      setSelected(new Set());
    } catch {
      // noop
    }
    setSending(false);
  };

  const pendingDrafts = drafts.filter((d) => d.status === "pending");
  const contextLabel = (ctx: string) =>
    ctx === "follow_up" ? "Follow-up" : ctx === "accepted" ? "New Partner" : ctx;
  const contextColor = (ctx: string) =>
    ctx === "accepted" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800";

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-base">Draft Messages</CardTitle>
            <p className="text-sm text-slate-500 mt-1">
              Review, edit, check, and batch send
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={loadDrafts}
              disabled={loading}
            >
              <RefreshCw className={`h-3 w-3 mr-1 ${loading ? "animate-spin" : ""}`} />
              Load
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={generateDrafts}
              disabled={generating}
            >
              {generating ? (
                <Loader2 className="h-3 w-3 animate-spin mr-1" />
              ) : (
                <RefreshCw className="h-3 w-3 mr-1" />
              )}
              Generate Drafts
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {pendingDrafts.length === 0 ? (
          <div className="text-center py-8">
            <Users className="h-10 w-10 mx-auto mb-3 text-slate-300" />
            <p className="text-sm text-slate-500">No pending drafts</p>
            <p className="text-xs text-slate-400 mt-1">
              Click &ldquo;Generate Drafts&rdquo; to create replies for all pending conversations
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {/* Batch controls */}
            <div className="flex items-center justify-between border-b pb-3">
              <button
                onClick={selectAll}
                className="flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900"
              >
                {selected.size === pendingDrafts.length ? (
                  <CheckSquare className="h-4 w-4 text-blue-600" />
                ) : (
                  <Square className="h-4 w-4" />
                )}
                {selected.size === pendingDrafts.length
                  ? "Deselect all"
                  : `Select all (${pendingDrafts.length})`}
              </button>

              <Button
                size="sm"
                onClick={batchSend}
                disabled={selected.size === 0 || sending}
              >
                {sending ? (
                  <Loader2 className="h-3 w-3 animate-spin mr-1" />
                ) : (
                  <Send className="h-3 w-3 mr-1" />
                )}
                Send {selected.size > 0 ? `(${selected.size})` : ""}
              </Button>
            </div>

            {/* Draft list */}
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {pendingDrafts.map((draft) => (
                <div
                  key={draft.draft_id}
                  className={`rounded-md border p-3 transition-colors ${
                    selected.has(draft.draft_id)
                      ? "border-blue-300 bg-blue-50"
                      : "border-slate-200"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {/* Checkbox */}
                    <button
                      onClick={() => toggleSelect(draft.draft_id)}
                      className="mt-0.5 flex-shrink-0"
                    >
                      {selected.has(draft.draft_id) ? (
                        <CheckSquare className="h-5 w-5 text-blue-600" />
                      ) : (
                        <Square className="h-5 w-5 text-slate-400" />
                      )}
                    </button>

                    <div className="flex-1 min-w-0">
                      {/* Creator info row */}
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm text-slate-900 truncate">
                          @{draft.creator_nickname}
                        </span>
                        <Badge className={`text-[10px] ${contextColor(draft.context)}`}>
                          {contextLabel(draft.context)}
                        </Badge>
                        {draft.creator_followers && (
                          <span className="text-[10px] text-slate-400">
                            {(draft.creator_followers / 1000).toFixed(1)}K
                          </span>
                        )}
                        {draft.creator_gmv_30d != null && (
                          <span className="text-[10px] text-slate-400">
                            ${draft.creator_gmv_30d.toFixed(0)}/mo
                          </span>
                        )}
                        {draft.context === "follow_up" && draft.days_pending > 0 && (
                          <span className="text-[10px] text-amber-500">
                            {draft.days_pending}d ago
                          </span>
                        )}
                      </div>

                      {/* Draft message */}
                      {editingId === draft.draft_id ? (
                        <div className="space-y-2">
                          <textarea
                            value={editText}
                            onChange={(e) => setEditText(e.target.value)}
                            className="w-full rounded-md border border-slate-300 p-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                            rows={3}
                            maxLength={500}
                          />
                          <div className="flex items-center gap-2">
                            <Button size="sm" onClick={saveEdit}>
                              <Check className="h-3 w-3 mr-1" /> Save
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => setEditingId(null)}
                            >
                              <X className="h-3 w-3 mr-1" /> Cancel
                            </Button>
                            <span className="text-xs text-slate-400">
                              {editText.length}/500
                            </span>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-start gap-2">
                          <p className="text-sm text-slate-700 flex-1">
                            {draft.draft_message}
                          </p>
                          <button
                            onClick={() => startEdit(draft)}
                            className="flex-shrink-0 p-1 rounded hover:bg-slate-100"
                            title="Edit draft"
                          >
                            <Edit3 className="h-3 w-3 text-slate-400" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
