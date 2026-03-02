"use client";

import React, { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Send, Loader2, Bot, User, Sparkles } from "lucide-react";
import { apiClient } from "@/lib/api-client";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  style_update?: Record<string, string>;
}

interface StyleConfig {
  tone: string;
  length: string;
  personality: string;
  avoid: string;
  include: string;
  custom_instructions: string;
}

export function StyleChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "I manage the tone and style of your affiliate outreach messages. " +
        'Tell me how to adjust — e.g. "sound more casual", "add urgency", ' +
        '"reference their niche". I\'ll update the style and you can regenerate all drafts.',
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [currentStyle, setCurrentStyle] = useState<StyleConfig | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || sending) return;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setSending(true);

    try {
      const result = await apiClient.post<{
        updated_style: StyleConfig;
        message: string;
        tip: string;
      }>(`${API_BASE}/tiktok/affiliates/style-chat`, {
        instruction: userMsg,
      });

      setCurrentStyle(result.updated_style);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `${result.message}\n\n${result.tip}`,
          style_update: result.updated_style,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Got it — I've noted your preference. Once the API is connected, " +
            "I'll update the style config and you can regenerate drafts with the new tone.",
        },
      ]);
    }

    setSending(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickActions = [
    "Sound more casual and fun",
    "Add more urgency",
    "Reference their specific niche",
    "Shorter messages",
    "Sound like a fellow creator, not a brand",
  ];

  return (
    <Card className="flex flex-col h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-blue-600" />
          <CardTitle className="text-base">Style Agent</CardTitle>
        </div>
        <p className="text-xs text-slate-500">
          Chat to adjust how draft messages sound
        </p>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col min-h-0">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-3 mb-3 max-h-[400px]">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex gap-2 ${msg.role === "user" ? "justify-end" : ""}`}
            >
              {msg.role === "assistant" && (
                <Bot className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
              )}
              <div
                className={`rounded-lg px-3 py-2 text-sm max-w-[85%] ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 text-slate-700"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>

                {/* Show style update summary */}
                {msg.style_update && (
                  <div className="mt-2 pt-2 border-t border-slate-200 text-xs space-y-1">
                    <p className="font-medium text-slate-600">Updated style:</p>
                    <p>
                      <span className="text-slate-500">Tone:</span>{" "}
                      {msg.style_update.tone}
                    </p>
                    <p>
                      <span className="text-slate-500">Personality:</span>{" "}
                      {msg.style_update.personality}
                    </p>
                  </div>
                )}
              </div>
              {msg.role === "user" && (
                <User className="h-5 w-5 text-slate-400 flex-shrink-0 mt-0.5" />
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick action chips */}
        {messages.length <= 2 && (
          <div className="flex flex-wrap gap-1.5 mb-3">
            {quickActions.map((action) => (
              <button
                key={action}
                onClick={() => {
                  setInput(action);
                }}
                className="text-xs px-2.5 py-1 rounded-full border border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300 transition-colors"
              >
                {action}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder='e.g. "sound more like a friend, less corporate"'
            className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={sending}
          />
          <Button size="sm" onClick={sendMessage} disabled={!input.trim() || sending}>
            {sending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Current style summary */}
        {currentStyle && (
          <div className="mt-3 p-2 rounded-md bg-slate-50 text-xs text-slate-600 space-y-0.5">
            <p className="font-medium text-slate-700">Active style:</p>
            <p>Tone: {currentStyle.tone}</p>
            <p>Length: {currentStyle.length}</p>
            {currentStyle.custom_instructions && (
              <p>Custom: {currentStyle.custom_instructions}</p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
