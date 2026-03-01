import { NextRequest, NextResponse } from "next/server";

const BACKEND_API_BASE = process.env.BACKEND_API_BASE || "http://localhost:8000";

/**
 * GET /api/tiktok/scripts - Retrieve saved scripts
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const channel = searchParams.get("channel");
    const status = searchParams.get("status");
    const limit = searchParams.get("limit") || "20";

    // Build query parameters
    const params = new URLSearchParams();
    if (channel) params.append("channel", channel);
    if (status) params.append("status", status);
    params.append("limit", limit);

    // Fetch from Python backend
    const response = await fetch(
      `${BACKEND_API_BASE}/api/tiktok-channels/scripts?${params.toString()}`,
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch scripts: ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching scripts:", error);
    return NextResponse.json(
      { error: "Failed to fetch scripts" },
      { status: 500 }
    );
  }
}

/**
 * POST /api/tiktok/scripts - Save a generated script
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Save to backend
    const response = await fetch(
      `${BACKEND_API_BASE}/api/tiktok-channels/scripts`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          channel: body.channel,
          topic: body.topic,
          product: body.product,
          script_content: body,
          status: "draft",
          metadata: {
            generated_at: body.generatedAt,
            estimated_length: body.estimatedLength,
            hashtags: body.hashtags,
          },
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to save script: ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json({ success: true, id: data.id });
  } catch (error) {
    console.error("Error saving script:", error);
    return NextResponse.json(
      { error: "Failed to save script" },
      { status: 500 }
    );
  }
}

/**
 * PUT /api/tiktok/scripts/[id] - Update a saved script
 */
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { id, ...updateData } = body;

    if (!id) {
      return NextResponse.json(
        { error: "Script ID is required" },
        { status: 400 }
      );
    }

    const response = await fetch(
      `${BACKEND_API_BASE}/api/tiktok-channels/scripts/${id}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updateData),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to update script: ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json({ success: true, data });
  } catch (error) {
    console.error("Error updating script:", error);
    return NextResponse.json(
      { error: "Failed to update script" },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/tiktok/scripts/[id] - Delete a script
 */
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get("id");

    if (!id) {
      return NextResponse.json(
        { error: "Script ID is required" },
        { status: 400 }
      );
    }

    const response = await fetch(
      `${BACKEND_API_BASE}/api/tiktok-channels/scripts/${id}`,
      {
        method: "DELETE",
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to delete script: ${response.statusText}`);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Error deleting script:", error);
    return NextResponse.json(
      { error: "Failed to delete script" },
      { status: 500 }
    );
  }
}