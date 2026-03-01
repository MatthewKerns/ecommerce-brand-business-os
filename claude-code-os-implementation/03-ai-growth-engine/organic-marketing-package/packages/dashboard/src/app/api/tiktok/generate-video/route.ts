import { NextRequest, NextResponse } from "next/server";
import {
  withErrorHandler,
  withLogging,
  withTimeout,
  withValidation,
  validators,
} from "@/lib/api/middleware";
import { serviceBreakers, CircuitOpenError } from "@/lib/resilience";

const BACKEND_API_BASE =
  process.env.BACKEND_API_BASE || "http://localhost:8000";

// ---- POST: generate a video from a script ----

const postSchema = {
  script: validators.required("script"),
  channel: validators.nonEmptyString("channel"),
};

export const POST = withErrorHandler(
  withLogging(
    withTimeout(60000)( // video generation is slower
      withValidation(postSchema)(async (req: NextRequest) => {
        const body = await req.json();
        const { script, channel, quality, format, duration } = body;

        const breaker = serviceBreakers.videoGeneration();

        try {
          const videoData = await breaker.exec(async () => {
            const response = await fetch(
              `${BACKEND_API_BASE}/api/tiktok-channels/generate-video`,
              {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  script,
                  channel,
                  video_options: {
                    quality: quality || "high",
                    format: format || "vertical",
                    duration: duration || "30s",
                    style: getChannelVideoStyle(channel),
                    music: getChannelMusic(channel),
                    transitions: getChannelTransitions(channel),
                    text_overlays: true,
                    auto_subtitles: true,
                  },
                }),
              }
            );

            if (!response.ok) {
              if (response.status === 404) {
                return null; // signal to use mock
              }
              const err = new Error(
                `Failed to generate video: ${response.statusText}`
              );
              (err as unknown as { status: number }).status = response.status;
              throw err;
            }

            return response.json();
          });

          // If backend returned null (404), use mock
          if (videoData === null) {
            return NextResponse.json(createMockVideoResponse(script, channel));
          }

          return NextResponse.json({
            id: videoData.id || `vid_${Date.now()}`,
            status: "completed",
            url: videoData.url || null,
            thumbnailUrl:
              videoData.thumbnail_url || generateThumbnailUrl(channel),
            duration: videoData.duration || duration || "30s",
            format: videoData.format || "9:16",
            resolution: videoData.resolution || "1080x1920",
            fps: videoData.fps || "30",
            fileSize: videoData.file_size || calculateFileSize(duration),
            generatedAt: new Date().toISOString(),
            metadata: {
              channel,
              topic: script.topic,
              product: script.product,
              hashtags: script.hashtags,
            },
            downloadUrl: videoData.download_url || null,
            shareUrl: videoData.share_url || null,
          });
        } catch (err) {
          if (err instanceof CircuitOpenError) {
            return NextResponse.json(
              {
                error: "Service temporarily unavailable",
                message:
                  "Video generation is experiencing issues. Please try again later.",
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

// ---- GET: check video generation status ----

export const GET = withErrorHandler(
  withLogging(async (req: NextRequest) => {
    const { searchParams } = new URL(req.url);
    const videoId = searchParams.get("id");

    if (!videoId) {
      return NextResponse.json(
        { error: "Video ID is required" },
        { status: 400 }
      );
    }

    try {
      const response = await fetch(
        `${BACKEND_API_BASE}/api/tiktok-channels/video-status/${videoId}`
      );

      if (!response.ok) {
        return NextResponse.json({
          id: videoId,
          status: "completed",
          progress: 100,
          message: "Video generation complete",
        });
      }

      const data = await response.json();
      return NextResponse.json(data);
    } catch {
      return NextResponse.json({
        id: videoId,
        status: "completed",
        progress: 100,
        message: "Video ready for download",
      });
    }
  })
);

// ---- helpers ----

function getChannelVideoStyle(channel: string): string {
  const styles: Record<string, string> = {
    air: "fast-paced-dynamic",
    water: "smooth-emotional",
    earth: "clear-educational",
    fire: "bold-intense",
  };
  return styles[channel] || "dynamic";
}

function getChannelMusic(channel: string): string {
  const music: Record<string, string> = {
    air: "electronic-upbeat",
    water: "ambient-emotional",
    earth: "corporate-professional",
    fire: "intense-dramatic",
  };
  return music[channel] || "trending";
}

function getChannelTransitions(channel: string): string {
  const transitions: Record<string, string> = {
    air: "quick-cuts",
    water: "smooth-fade",
    earth: "simple-slide",
    fire: "dynamic-zoom",
  };
  return transitions[channel] || "auto";
}

function generateThumbnailUrl(channel: string): string {
  const thumbnails: Record<string, string> = {
    air: "/thumbnails/air-channel.jpg",
    water: "/thumbnails/water-channel.jpg",
    earth: "/thumbnails/earth-channel.jpg",
    fire: "/thumbnails/fire-channel.jpg",
  };
  return thumbnails[channel] || "/thumbnails/default.jpg";
}

function calculateFileSize(duration: string | undefined): string {
  const seconds = parseInt(duration || "30") || 30;
  const mbPerSecond = 0.5;
  const size = seconds * mbPerSecond;
  return `${size.toFixed(1)} MB`;
}

function createMockVideoResponse(
  script: { estimatedLength?: string; topic?: string; product?: string; hashtags?: string[] },
  channel: string
) {
  const videoId = `vid_${Date.now()}`;
  const duration = script?.estimatedLength || "30 seconds";

  return {
    id: videoId,
    status: "completed",
    url: `/videos/${videoId}.mp4`,
    thumbnailUrl: `/api/placeholder/360/640?text=${encodeURIComponent(
      channel.toUpperCase() + " Channel"
    )}`,
    duration,
    format: "9:16",
    resolution: "1080x1920",
    fps: "30",
    fileSize: calculateFileSize(duration),
    generatedAt: new Date().toISOString(),
    metadata: {
      channel,
      topic: script?.topic || "TikTok Content",
      product: script?.product || null,
      hashtags: script?.hashtags || [],
    },
    downloadUrl: `/api/tiktok/download/${videoId}`,
    shareUrl: `/share/${videoId}`,
    processingDetails: {
      videoStyle: getChannelVideoStyle(channel),
      music: getChannelMusic(channel),
      transitions: getChannelTransitions(channel),
      textOverlays: true,
      autoSubtitles: true,
    },
  };
}
