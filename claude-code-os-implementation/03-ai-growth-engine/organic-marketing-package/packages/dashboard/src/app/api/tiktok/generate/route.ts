import { NextRequest, NextResponse } from "next/server";
import {
  withErrorHandler,
  withLogging,
  withTimeout,
  withValidation,
  validators,
} from "@/lib/api/middleware";
import { serviceBreakers, CircuitOpenError } from "@/lib/resilience";

// TikTok API endpoint from Python backend
const TIKTOK_API_BASE = process.env.TIKTOK_API_BASE || "http://localhost:8000";

const bodySchema = {
  channel_element: validators.nonEmptyString("channel_element"),
  topic: validators.nonEmptyString("topic"),
  product: validators.optional(validators.string("product")),
  include_product_link: validators.optional(validators.boolean("include_product_link")),
};

export const POST = withErrorHandler(
  withLogging(
    withTimeout(30000)(
      withValidation(bodySchema)(async (req: NextRequest) => {
        const body = await req.json();
        const {
          channel_element,
          topic,
          product,
          include_product_link,
          additional_hashtags,
        } = body;

        const breaker = serviceBreakers.tiktok();

        try {
          const data = await breaker.exec(async () => {
            const response = await fetch(
              `${TIKTOK_API_BASE}/api/tiktok-channels/generate-script`,
              {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  channel_element,
                  topic,
                  product: product || null,
                  include_product_link: include_product_link || false,
                  additional_hashtags: additional_hashtags || [],
                }),
              }
            );

            if (!response.ok) {
              const errorText = await response.text();
              // eslint-disable-next-line no-console
              console.error("Python backend error:", errorText);
              const err = new Error(
                `Failed to generate script: ${response.statusText}`
              );
              (err as unknown as { status: number }).status = response.status;
              throw err;
            }

            return response.json();
          });

          const transformedScript = transformScriptFormat(data, {
            channel: channel_element,
            topic,
            product,
          });

          return NextResponse.json(transformedScript);
        } catch (err) {
          if (err instanceof CircuitOpenError) {
            return NextResponse.json(
              {
                error: "Service temporarily unavailable",
                message:
                  "The TikTok script generation service is experiencing issues. Please try again later.",
                retryAfter: err.nextRetryAt.toISOString(),
              },
              { status: 503 }
            );
          }
          throw err;
        }
      })
    )
  )
);

/**
 * Transform the Python backend response to our frontend format
 */
function transformScriptFormat(
  backendData: { script: string; file_path?: string },
  metadata: { channel: string; topic: string; product?: string }
) {
  const sections = parseScriptSections(backendData.script);
  const hashtags = extractHashtags(backendData.script);
  const productionNotes = extractProductionNotes(backendData.script);
  const caption = extractCaption(backendData.script);

  return {
    channel: metadata.channel,
    topic: metadata.topic,
    product: metadata.product,
    sections,
    productionNotes,
    caption,
    hashtags,
    estimatedLength: getEstimatedLength(metadata.channel),
    generatedAt: new Date().toISOString(),
    filePath: backendData.file_path,
  };
}

interface ScriptSection {
  type: string;
  timeRange?: string;
  visual: string;
  audio: string;
  textOverlay: string;
  notes?: string;
}

function parseScriptSections(script: string): ScriptSection[] {
  const sections: ScriptSection[] = [];
  const lines = script.split("\n");

  let currentSection: ScriptSection | null = null;

  for (const line of lines) {
    if (line.startsWith("[HOOK") || line.includes("HOOK (")) {
      if (currentSection) sections.push(currentSection);
      currentSection = {
        type: "HOOK",
        timeRange: extractTimeRange(line),
        visual: "",
        audio: "",
        textOverlay: "",
      };
    } else if (line.startsWith("[MAIN") || line.includes("MAIN CONTENT")) {
      if (currentSection) sections.push(currentSection);
      currentSection = {
        type: "MAIN CONTENT",
        timeRange: extractTimeRange(line),
        visual: "",
        audio: "",
        textOverlay: "",
      };
    } else if (
      line.startsWith("[PRODUCT") ||
      line.includes("PRODUCT INTEGRATION")
    ) {
      if (currentSection) sections.push(currentSection);
      currentSection = {
        type: "PRODUCT INTEGRATION",
        timeRange: extractTimeRange(line),
        visual: "",
        audio: "",
        textOverlay: "",
      };
    } else if (line.startsWith("[CALL-TO-ACTION") || line.includes("CTA")) {
      if (currentSection) sections.push(currentSection);
      currentSection = {
        type: "CALL-TO-ACTION",
        timeRange: extractTimeRange(line),
        visual: "",
        audio: "",
        textOverlay: "",
      };
    } else if (currentSection) {
      if (line.startsWith("Visual:")) {
        currentSection.visual = line.substring(7).trim();
      } else if (line.startsWith("Audio:")) {
        currentSection.audio = line.substring(6).trim();
      } else if (line.startsWith("Text Overlay:")) {
        currentSection.textOverlay = line.substring(13).trim();
      } else if (line.startsWith("Note:") || line.startsWith("Tip:")) {
        currentSection.notes = line.trim();
      }
    }
  }

  if (currentSection) sections.push(currentSection);

  if (sections.length === 0) {
    sections.push({
      type: "FULL SCRIPT",
      visual: "See full script for details",
      audio: script.substring(0, 500),
      textOverlay: "Generated script",
    });
  }

  return sections;
}

function extractTimeRange(line: string): string {
  const match = line.match(/\(([0-9\-]+s?)\)/);
  return match ? match[1] ?? "" : "";
}

function extractHashtags(script: string): string[] {
  const hashtagSection = script.match(/\[HASHTAGS?\][\s\S]*?(?=\[|$)/i);
  if (!hashtagSection) {
    const captionSection = script.match(/\[CAPTION[\s\S]*?(?=\[|$)/i);
    if (captionSection) {
      return captionSection[0].match(/#\w+/g) || [];
    }
    return ["#InfinityVault", "#TCG", "#TradingCards", "#CardGame"];
  }
  return hashtagSection[0].match(/#\w+/g) || [];
}

function extractProductionNotes(
  script: string
): Record<string, string> {
  const notes: Record<string, string> = {};
  const productionSection = script.match(
    /\[PRODUCTION NOTES?\][\s\S]*?(?=\[|$)/i
  );
  if (productionSection) {
    const content = productionSection[0];
    const musicMatch = content.match(/Music.*?:(.+)/i);
    if (musicMatch?.[1]) notes.musicStyle = musicMatch[1].trim();
    const paceMatch = content.match(/Pace.*?:(.+)/i);
    if (paceMatch?.[1]) notes.pace = paceMatch[1].trim();
    const transitionsMatch = content.match(/Transitions?.*?:(.+)/i);
    if (transitionsMatch?.[1]) notes.transitions = transitionsMatch[1].trim();
  }
  return notes;
}

function extractCaption(script: string): string {
  const captionSection = script.match(/\[CAPTION[\s\S]*?(?=\[|#)/i);
  if (captionSection) {
    let caption = captionSection[0]
      .replace(/\[CAPTION.*?\]/i, "")
      .replace(/#\w+/g, "")
      .trim();
    caption = caption.replace(/^["']|["']$/g, "");
    return caption || "Check out this amazing content!";
  }
  return "New video alert! Don't miss this one";
}

function getEstimatedLength(channel: string): string {
  const lengths: Record<string, string> = {
    air: "15-30 seconds",
    water: "30-60 seconds",
    earth: "30-45 seconds",
    fire: "15-30 seconds",
  };
  return lengths[channel] || "30 seconds";
}
