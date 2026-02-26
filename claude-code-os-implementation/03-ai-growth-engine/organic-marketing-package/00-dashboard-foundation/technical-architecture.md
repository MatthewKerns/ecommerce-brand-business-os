# Dashboard Technical Architecture

## Overview

This document defines the technical implementation architecture for the Organic Marketing Dashboard Foundation. It provides detailed specifications for developers to build a scalable, maintainable, and performant web application using Next.js 14+, React, and modern web technologies.

## Technology Stack

### Core Framework
```yaml
Frontend:
  Framework: Next.js 14.2+ (App Router)
  Language: TypeScript 5.3+
  Runtime: Node.js 20 LTS
  Package Manager: pnpm (preferred) or npm

UI Layer:
  Components: React 18.3+
  Styling: Tailwind CSS 3.4+
  Component Library: shadcn/ui (Radix UI primitives)
  Icons: Lucide React
  Animations: Framer Motion 11+

State Management:
  Global State: Zustand 4.5+
  Server State: TanStack Query 5+ (React Query)
  Form State: React Hook Form 7.5+
  Validation: Zod 3.22+

Data Visualization:
  Charts: Recharts 2.10+
  Advanced: D3.js 7+ (for custom visualizations)
  Tables: TanStack Table 8+
```

### Backend Integration
```yaml
API Layer:
  Type-Safe API: tRPC 10.45+
  REST Fallback: Next.js API Routes
  Real-time: Server-Sent Events (SSE)
  WebSockets: Socket.io (future)

Database:
  Primary: PostgreSQL 16+
  ORM: Prisma 5.9+
  Migrations: Prisma Migrate
  Connection Pooling: PgBouncer

Caching:
  Primary: Redis 7+
  Client: ioredis
  Session Store: connect-redis
  Cache Strategy: LRU with TTL

Queue System:
  Queue Manager: BullMQ 5+
  Redis Backend: Same Redis instance
  Workers: Separate Node processes

File Storage:
  Provider: AWS S3 or Cloudflare R2
  SDK: AWS SDK v3
  CDN: Cloudflare
```

### Authentication & Security
```yaml
Authentication:
  Provider: Clerk 4.29+
  Session Management: Clerk Session Tokens
  Multi-tenancy: Workspace-based
  SSO: OAuth providers via Clerk

Security:
  CORS: Configured per environment
  CSP: Strict Content Security Policy
  Rate Limiting: express-rate-limit
  API Keys: Custom implementation
  Encryption: bcrypt for hashes, AES for sensitive data
```

## Project Structure

```
/dashboard
├── /app                      # Next.js App Router
│   ├── /(auth)              # Auth routes group
│   │   ├── /sign-in
│   │   ├── /sign-up
│   │   └── /sign-out
│   ├── /(dashboard)         # Authenticated routes group
│   │   ├── /page.tsx        # Dashboard overview
│   │   ├── /content         # Content management
│   │   ├── /email           # Email marketing
│   │   ├── /analytics       # Analytics section
│   │   ├── /integrations    # External integrations
│   │   └── /settings        # Settings pages
│   ├── /api                 # API routes
│   │   └── /trpc           # tRPC router
│   ├── layout.tsx          # Root layout
│   └── globals.css         # Global styles
│
├── /components              # React components
│   ├── /ui                 # shadcn/ui components
│   ├── /dashboard          # Dashboard-specific components
│   ├── /content            # Content management components
│   ├── /email              # Email marketing components
│   ├── /analytics          # Analytics components
│   └── /shared             # Shared components
│
├── /lib                    # Utility libraries
│   ├── /api               # API client utilities
│   ├── /auth              # Auth utilities
│   ├── /db                # Database utilities
│   ├── /redis             # Redis client
│   ├── /queue             # Queue utilities
│   └── /utils             # General utilities
│
├── /server                 # Server-side code
│   ├── /api               # API implementation
│   │   ├── /routers      # tRPC routers
│   │   └── /procedures   # tRPC procedures
│   ├── /db                # Database layer
│   │   ├── /schema       # Prisma schema
│   │   └── /migrations   # Database migrations
│   ├── /queue             # Queue workers
│   └── /services          # Business logic services
│
├── /hooks                  # Custom React hooks
├── /store                  # Zustand stores
├── /types                  # TypeScript type definitions
├── /config                 # Configuration files
├── /public                 # Static assets
└── /tests                  # Test files
```

## Database Schema

### Core Tables

```sql
-- Users table (managed by Clerk, reference only)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clerk_id VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  avatar_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Workspaces table
CREATE TABLE workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(255) UNIQUE NOT NULL,
  logo_url TEXT,
  owner_id UUID REFERENCES users(id),
  settings JSONB DEFAULT '{}',
  subscription_tier VARCHAR(50) DEFAULT 'free',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Workspace members junction table
CREATE TABLE workspace_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role VARCHAR(50) NOT NULL CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
  invited_by UUID REFERENCES users(id),
  joined_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(workspace_id, user_id)
);

-- API keys table
CREATE TABLE api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  key_hash VARCHAR(255) UNIQUE NOT NULL,
  last_used_at TIMESTAMP,
  expires_at TIMESTAMP,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  revoked_at TIMESTAMP
);

-- Content table
CREATE TABLE content (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL CHECK (type IN ('tiktok', 'blog', 'email')),
  status VARCHAR(50) NOT NULL DEFAULT 'draft',
  title VARCHAR(500) NOT NULL,
  body TEXT,
  media_urls JSONB DEFAULT '[]',
  metadata JSONB DEFAULT '{}',
  scheduled_at TIMESTAMP,
  published_at TIMESTAMP,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Content metrics table
CREATE TABLE content_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content_id UUID REFERENCES content(id) ON DELETE CASCADE,
  views INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  saves INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  conversions INTEGER DEFAULT 0,
  revenue DECIMAL(10, 2) DEFAULT 0,
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(content_id)
);

-- Email campaigns table
CREATE TABLE email_campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(50) NOT NULL CHECK (type IN ('one-time', 'sequence', 'triggered')),
  status VARCHAR(50) NOT NULL DEFAULT 'draft',
  segment_criteria JSONB DEFAULT '{}',
  content JSONB NOT NULL,
  schedule JSONB,
  metrics JSONB DEFAULT '{}',
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Leads table
CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
  email VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  tags TEXT[] DEFAULT '{}',
  source VARCHAR(255),
  status VARCHAR(50) DEFAULT 'active',
  custom_fields JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(workspace_id, email)
);

-- Activity log table
CREATE TABLE activity_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id),
  action VARCHAR(255) NOT NULL,
  entity_type VARCHAR(50),
  entity_id UUID,
  metadata JSONB DEFAULT '{}',
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_workspaces_slug ON workspaces(slug);
CREATE INDEX idx_workspace_members_workspace_id ON workspace_members(workspace_id);
CREATE INDEX idx_workspace_members_user_id ON workspace_members(user_id);
CREATE INDEX idx_content_workspace_id ON content(workspace_id);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_scheduled_at ON content(scheduled_at);
CREATE INDEX idx_email_campaigns_workspace_id ON email_campaigns(workspace_id);
CREATE INDEX idx_leads_workspace_id ON leads(workspace_id);
CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_activity_logs_workspace_id ON activity_logs(workspace_id);
CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at DESC);
```

## API Architecture

### tRPC Router Structure

```typescript
// server/api/root.ts
import { createTRPCRouter } from "./trpc";
import { authRouter } from "./routers/auth";
import { workspaceRouter } from "./routers/workspace";
import { contentRouter } from "./routers/content";
import { emailRouter } from "./routers/email";
import { analyticsRouter } from "./routers/analytics";
import { integrationsRouter } from "./routers/integrations";

export const appRouter = createTRPCRouter({
  auth: authRouter,
  workspace: workspaceRouter,
  content: contentRouter,
  email: emailRouter,
  analytics: analyticsRouter,
  integrations: integrationsRouter,
});

export type AppRouter = typeof appRouter;
```

### Example tRPC Procedure

```typescript
// server/api/routers/content.ts
import { z } from "zod";
import { createTRPCRouter, protectedProcedure } from "../trpc";

export const contentRouter = createTRPCRouter({
  // List content with pagination
  list: protectedProcedure
    .input(z.object({
      workspaceId: z.string().uuid(),
      type: z.enum(['tiktok', 'blog', 'email']).optional(),
      status: z.enum(['draft', 'scheduled', 'published']).optional(),
      limit: z.number().min(1).max(100).default(20),
      offset: z.number().min(0).default(0),
    }))
    .query(async ({ ctx, input }) => {
      const content = await ctx.db.content.findMany({
        where: {
          workspaceId: input.workspaceId,
          ...(input.type && { type: input.type }),
          ...(input.status && { status: input.status }),
        },
        take: input.limit,
        skip: input.offset,
        orderBy: { createdAt: 'desc' },
        include: {
          metrics: true,
          createdBy: {
            select: { id: true, name: true, avatarUrl: true },
          },
        },
      });

      const total = await ctx.db.content.count({
        where: {
          workspaceId: input.workspaceId,
          ...(input.type && { type: input.type }),
          ...(input.status && { status: input.status }),
        },
      });

      return { content, total };
    }),

  // Create new content
  create: protectedProcedure
    .input(z.object({
      workspaceId: z.string().uuid(),
      type: z.enum(['tiktok', 'blog', 'email']),
      title: z.string().min(1).max(500),
      body: z.string(),
      mediaUrls: z.array(z.string().url()).optional(),
      scheduledAt: z.date().optional(),
    }))
    .mutation(async ({ ctx, input }) => {
      // Check workspace membership
      const membership = await ctx.db.workspaceMember.findFirst({
        where: {
          workspaceId: input.workspaceId,
          userId: ctx.session.userId,
        },
      });

      if (!membership || membership.role === 'viewer') {
        throw new Error('Unauthorized');
      }

      const content = await ctx.db.content.create({
        data: {
          workspaceId: input.workspaceId,
          type: input.type,
          title: input.title,
          body: input.body,
          mediaUrls: input.mediaUrls || [],
          scheduledAt: input.scheduledAt,
          status: input.scheduledAt ? 'scheduled' : 'draft',
          createdBy: ctx.session.userId,
        },
      });

      // Queue for processing if scheduled
      if (input.scheduledAt) {
        await ctx.queue.add('publish-content', {
          contentId: content.id,
        }, {
          delay: input.scheduledAt.getTime() - Date.now(),
        });
      }

      return content;
    }),

  // Generate AI content
  generate: protectedProcedure
    .input(z.object({
      workspaceId: z.string().uuid(),
      platform: z.enum(['tiktok', 'blog', 'email']),
      product: z.string(),
      contentType: z.enum(['demo', 'tutorial', 'review', 'comparison', 'tips', 'story']),
      tone: z.enum(['casual', 'professional', 'humorous', 'educational']),
      length: z.enum(['short', 'medium', 'long']),
      context: z.string().optional(),
    }))
    .mutation(async ({ ctx, input }) => {
      // Queue content generation job
      const job = await ctx.queue.add('generate-content', {
        ...input,
        userId: ctx.session.userId,
      });

      // Return job ID for status tracking
      return { jobId: job.id };
    }),
});
```

### REST API Endpoints (Fallback)

```typescript
// app/api/health/route.ts
import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { redis } from '@/lib/redis';

export async function GET() {
  try {
    // Check database
    await db.$queryRaw`SELECT 1`;
    const dbHealthy = true;

    // Check Redis
    await redis.ping();
    const redisHealthy = true;

    // Check external services
    const services = await Promise.allSettled([
      checkTikTokAPI(),
      checkGmailAPI(),
      checkAmazonMCF(),
      checkOpenAI(),
    ]);

    return NextResponse.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        database: dbHealthy,
        redis: redisHealthy,
        tiktok: services[0].status === 'fulfilled',
        gmail: services[1].status === 'fulfilled',
        amazon: services[2].status === 'fulfilled',
        openai: services[3].status === 'fulfilled',
      },
    });
  } catch (error) {
    return NextResponse.json(
      { status: 'unhealthy', error: error.message },
      { status: 503 }
    );
  }
}
```

## Authentication Flow

### Clerk Integration

```typescript
// middleware.ts
import { authMiddleware } from "@clerk/nextjs";

export default authMiddleware({
  publicRoutes: [
    "/",
    "/sign-in",
    "/sign-up",
    "/api/health",
    "/api/webhook/clerk",
  ],
  afterAuth(auth, req, evt) {
    // Handle users who aren't authenticated
    if (!auth.userId && !auth.isPublicRoute) {
      const signInUrl = new URL('/sign-in', req.url);
      signInUrl.searchParams.set('redirect_url', req.url);
      return Response.redirect(signInUrl);
    }

    // Redirect users to workspace selection if no workspace in session
    if (auth.userId && !auth.sessionClaims?.workspace &&
        !req.url.includes('/workspaces')) {
      return Response.redirect(new URL('/workspaces', req.url));
    }
  },
});

export const config = {
  matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
};
```

### Session Management

```typescript
// lib/auth/session.ts
import { auth } from '@clerk/nextjs';
import { db } from '@/lib/db';

export async function getCurrentUser() {
  const { userId } = auth();
  if (!userId) return null;

  const user = await db.user.findUnique({
    where: { clerkId: userId },
    include: {
      workspaces: {
        include: {
          workspace: true,
        },
      },
    },
  });

  return user;
}

export async function getCurrentWorkspace() {
  const user = await getCurrentUser();
  if (!user) return null;

  const workspaceId = getWorkspaceFromSession();
  if (!workspaceId) return null;

  const membership = user.workspaces.find(
    (m) => m.workspaceId === workspaceId
  );

  return membership?.workspace || null;
}

export async function requireWorkspaceAccess(
  workspaceId: string,
  minRole: 'viewer' | 'member' | 'admin' | 'owner' = 'viewer'
) {
  const user = await getCurrentUser();
  if (!user) throw new Error('Unauthorized');

  const membership = await db.workspaceMember.findFirst({
    where: {
      workspaceId,
      userId: user.id,
    },
  });

  if (!membership) throw new Error('Access denied');

  const roleHierarchy = {
    viewer: 0,
    member: 1,
    admin: 2,
    owner: 3,
  };

  if (roleHierarchy[membership.role] < roleHierarchy[minRole]) {
    throw new Error('Insufficient permissions');
  }

  return membership;
}
```

## State Management

### Zustand Store Example

```typescript
// store/workspace.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface WorkspaceState {
  currentWorkspace: Workspace | null;
  workspaces: Workspace[];
  setCurrentWorkspace: (workspace: Workspace) => void;
  setWorkspaces: (workspaces: Workspace[]) => void;
  switchWorkspace: (workspaceId: string) => Promise<void>;
}

export const useWorkspaceStore = create<WorkspaceState>()(
  persist(
    (set, get) => ({
      currentWorkspace: null,
      workspaces: [],

      setCurrentWorkspace: (workspace) =>
        set({ currentWorkspace: workspace }),

      setWorkspaces: (workspaces) =>
        set({ workspaces }),

      switchWorkspace: async (workspaceId) => {
        const workspace = get().workspaces.find(w => w.id === workspaceId);
        if (!workspace) throw new Error('Workspace not found');

        // Update session with new workspace
        await fetch('/api/workspace/switch', {
          method: 'POST',
          body: JSON.stringify({ workspaceId }),
        });

        set({ currentWorkspace: workspace });
      },
    }),
    {
      name: 'workspace-storage',
      partialize: (state) => ({
        currentWorkspace: state.currentWorkspace
      }),
    }
  )
);
```

### React Query Configuration

```typescript
// lib/api/query-client.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 10, // 10 minutes
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Custom hooks
export function useContent(workspaceId: string) {
  return useQuery({
    queryKey: ['content', workspaceId],
    queryFn: () => api.content.list({ workspaceId }),
    enabled: !!workspaceId,
  });
}

export function useCreateContent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateContentInput) => api.content.create(data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries(['content', variables.workspaceId]);
      toast.success('Content created successfully');
    },
    onError: (error) => {
      toast.error('Failed to create content');
      console.error(error);
    },
  });
}
```

## Queue Processing

### BullMQ Configuration

```typescript
// lib/queue/index.ts
import { Queue, Worker } from 'bullmq';
import { redis } from '@/lib/redis';

// Create queues
export const contentQueue = new Queue('content', {
  connection: redis,
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000,
    },
    removeOnComplete: true,
    removeOnFail: false,
  },
});

export const emailQueue = new Queue('email', {
  connection: redis,
  defaultJobOptions: {
    attempts: 5,
    backoff: {
      type: 'exponential',
      delay: 5000,
    },
  },
});

export const analyticsQueue = new Queue('analytics', {
  connection: redis,
  defaultJobOptions: {
    attempts: 1,
    removeOnComplete: true,
  },
});
```

### Worker Implementation

```typescript
// workers/content.worker.ts
import { Worker, Job } from 'bullmq';
import { redis } from '@/lib/redis';
import { generateContent } from '@/services/ai';
import { publishToTikTok } from '@/services/tiktok';
import { db } from '@/lib/db';

const contentWorker = new Worker(
  'content',
  async (job: Job) => {
    switch (job.name) {
      case 'generate-content':
        return await handleGenerateContent(job);
      case 'publish-content':
        return await handlePublishContent(job);
      case 'sync-metrics':
        return await handleSyncMetrics(job);
      default:
        throw new Error(`Unknown job type: ${job.name}`);
    }
  },
  {
    connection: redis,
    concurrency: 5,
  }
);

async function handleGenerateContent(job: Job) {
  const { platform, product, contentType, tone, length, context, userId, workspaceId } = job.data;

  try {
    // Generate content using AI
    const generated = await generateContent({
      platform,
      product,
      contentType,
      tone,
      length,
      context,
    });

    // Save to database
    const content = await db.content.create({
      data: {
        workspaceId,
        type: platform,
        title: generated.title,
        body: generated.body,
        status: 'draft',
        createdBy: userId,
        metadata: {
          ai_generated: true,
          generation_params: job.data,
        },
      },
    });

    // Send notification
    await notifyUser(userId, {
      title: 'Content Generated',
      message: `Your ${platform} content is ready for review`,
      link: `/content/${content.id}`,
    });

    return content;
  } catch (error) {
    console.error('Content generation failed:', error);
    throw error;
  }
}

async function handlePublishContent(job: Job) {
  const { contentId } = job.data;

  const content = await db.content.findUnique({
    where: { id: contentId },
    include: { workspace: true },
  });

  if (!content) throw new Error('Content not found');

  try {
    // Publish based on platform
    let result;
    switch (content.type) {
      case 'tiktok':
        result = await publishToTikTok(content);
        break;
      case 'blog':
        result = await publishToBlog(content);
        break;
      case 'email':
        result = await sendEmail(content);
        break;
    }

    // Update status
    await db.content.update({
      where: { id: contentId },
      data: {
        status: 'published',
        publishedAt: new Date(),
        metadata: {
          ...content.metadata,
          publish_result: result,
        },
      },
    });

    return result;
  } catch (error) {
    await db.content.update({
      where: { id: contentId },
      data: {
        status: 'failed',
        metadata: {
          ...content.metadata,
          error: error.message,
        },
      },
    });
    throw error;
  }
}

// Start worker
contentWorker.on('completed', (job) => {
  console.log(`Job ${job.id} completed successfully`);
});

contentWorker.on('failed', (job, err) => {
  console.error(`Job ${job?.id} failed:`, err);
});

export default contentWorker;
```

## Caching Strategy

### Redis Cache Implementation

```typescript
// lib/cache/index.ts
import { redis } from '@/lib/redis';

export class Cache {
  private prefix: string;
  private ttl: number;

  constructor(prefix: string, ttl: number = 3600) {
    this.prefix = prefix;
    this.ttl = ttl;
  }

  private key(id: string): string {
    return `${this.prefix}:${id}`;
  }

  async get<T>(id: string): Promise<T | null> {
    const data = await redis.get(this.key(id));
    return data ? JSON.parse(data) : null;
  }

  async set<T>(id: string, value: T, ttl?: number): Promise<void> {
    await redis.setex(
      this.key(id),
      ttl || this.ttl,
      JSON.stringify(value)
    );
  }

  async del(id: string): Promise<void> {
    await redis.del(this.key(id));
  }

  async invalidate(pattern: string): Promise<void> {
    const keys = await redis.keys(`${this.prefix}:${pattern}`);
    if (keys.length > 0) {
      await redis.del(...keys);
    }
  }
}

// Cache instances
export const contentCache = new Cache('content', 300); // 5 minutes
export const analyticsCache = new Cache('analytics', 3600); // 1 hour
export const userCache = new Cache('user', 1800); // 30 minutes
```

### Query Result Caching

```typescript
// lib/cache/query-cache.ts
export async function cachedQuery<T>(
  key: string,
  queryFn: () => Promise<T>,
  ttl: number = 300
): Promise<T> {
  // Try cache first
  const cached = await redis.get(key);
  if (cached) {
    return JSON.parse(cached);
  }

  // Execute query
  const result = await queryFn();

  // Cache result
  await redis.setex(key, ttl, JSON.stringify(result));

  return result;
}

// Usage example
export async function getWorkspaceMetrics(workspaceId: string) {
  return cachedQuery(
    `metrics:${workspaceId}`,
    async () => {
      const [content, email, leads] = await Promise.all([
        db.content.count({ where: { workspaceId } }),
        db.emailCampaign.count({ where: { workspaceId } }),
        db.lead.count({ where: { workspaceId } }),
      ]);

      return { content, email, leads };
    },
    600 // 10 minutes
  );
}
```

## Real-time Updates

### Server-Sent Events (SSE)

```typescript
// app/api/sse/route.ts
import { NextRequest } from 'next/server';

export async function GET(request: NextRequest) {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      const sendEvent = (data: any) => {
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify(data)}\n\n`)
        );
      };

      // Send initial connection event
      sendEvent({ type: 'connected', timestamp: new Date() });

      // Subscribe to Redis pub/sub
      const subscriber = redis.duplicate();
      await subscriber.connect();

      subscriber.on('message', (channel, message) => {
        sendEvent({
          type: 'update',
          channel,
          data: JSON.parse(message)
        });
      });

      await subscriber.subscribe('dashboard:updates');

      // Keep connection alive
      const keepAlive = setInterval(() => {
        sendEvent({ type: 'ping', timestamp: new Date() });
      }, 30000);

      // Cleanup on disconnect
      request.signal.addEventListener('abort', () => {
        clearInterval(keepAlive);
        subscriber.disconnect();
      });
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
```

### Client SSE Hook

```typescript
// hooks/useSSE.ts
import { useEffect, useState } from 'react';

export function useSSE(url: string) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const eventSource = new EventSource(url);

    eventSource.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setData(parsed);
      } catch (err) {
        setError(err);
      }
    };

    eventSource.onerror = (err) => {
      setError(err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [url]);

  return { data, error };
}

// Usage
function DashboardMetrics() {
  const { data } = useSSE('/api/sse');

  useEffect(() => {
    if (data?.type === 'update') {
      // Update local state or refetch queries
      queryClient.invalidateQueries(['metrics']);
    }
  }, [data]);

  return <MetricsDisplay />;
}
```

## Error Handling

### Global Error Handler

```typescript
// lib/errors/handler.ts
import { TRPCError } from '@trpc/server';
import { ZodError } from 'zod';
import * as Sentry from '@sentry/nextjs';

export class AppError extends Error {
  statusCode: number;
  isOperational: boolean;

  constructor(
    message: string,
    statusCode: number = 500,
    isOperational: boolean = true
  ) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    Error.captureStackTrace(this, this.constructor);
  }
}

export function handleError(error: unknown): TRPCError {
  // Log to Sentry
  Sentry.captureException(error);

  if (error instanceof ZodError) {
    return new TRPCError({
      code: 'BAD_REQUEST',
      message: 'Validation error',
      cause: error.flatten(),
    });
  }

  if (error instanceof AppError) {
    return new TRPCError({
      code: error.statusCode === 404 ? 'NOT_FOUND' : 'INTERNAL_SERVER_ERROR',
      message: error.message,
    });
  }

  // Default error
  return new TRPCError({
    code: 'INTERNAL_SERVER_ERROR',
    message: 'An unexpected error occurred',
  });
}
```

### Error Boundary

```typescript
// components/ErrorBoundary.tsx
import { ErrorBoundary } from 'react-error-boundary';
import { useRouter } from 'next/navigation';

function ErrorFallback({ error, resetErrorBoundary }) {
  const router = useRouter();

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Something went wrong</h1>
        <p className="text-gray-600 mb-8">{error.message}</p>
        <div className="space-x-4">
          <button
            onClick={resetErrorBoundary}
            className="px-4 py-2 bg-blue-500 text-white rounded"
          >
            Try again
          </button>
          <button
            onClick={() => router.push('/')}
            className="px-4 py-2 bg-gray-500 text-white rounded"
          >
            Go home
          </button>
        </div>
      </div>
    </div>
  );
}

export function AppErrorBoundary({ children }) {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onReset={() => window.location.reload()}
      onError={(error) => {
        console.error('Error boundary caught:', error);
        Sentry.captureException(error);
      }}
    >
      {children}
    </ErrorBoundary>
  );
}
```

## Performance Optimization

### Next.js Optimization

```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  images: {
    domains: ['images.clerk.dev', 'res.cloudinary.com'],
    formats: ['image/avif', 'image/webp'],
  },

  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['@shadcn/ui', 'lucide-react'],
  },

  // Enable compression
  compress: true,

  // Headers for caching
  async headers() {
    return [
      {
        source: '/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },

  // Redirects
  async redirects() {
    return [
      {
        source: '/dashboard',
        destination: '/',
        permanent: true,
      },
    ];
  },
};

module.exports = nextConfig;
```

### Component Code Splitting

```typescript
// components/LazyComponents.tsx
import dynamic from 'next/dynamic';

// Lazy load heavy components
export const ChartComponent = dynamic(
  () => import('./analytics/ChartComponent'),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-64 rounded" />,
    ssr: false,
  }
);

export const EmailEditor = dynamic(
  () => import('./email/EmailEditor'),
  {
    loading: () => <div>Loading editor...</div>,
    ssr: false,
  }
);

export const ContentCalendar = dynamic(
  () => import('./content/ContentCalendar'),
  {
    loading: () => <div>Loading calendar...</div>,
  }
);
```

### Database Query Optimization

```typescript
// lib/db/optimized-queries.ts
import { db } from '@/lib/db';

// Use select to reduce payload
export async function getContentList(workspaceId: string) {
  return db.content.findMany({
    where: { workspaceId },
    select: {
      id: true,
      title: true,
      type: true,
      status: true,
      scheduledAt: true,
      createdAt: true,
      createdBy: {
        select: { name: true, avatarUrl: true },
      },
    },
    orderBy: { createdAt: 'desc' },
    take: 20,
  });
}

// Use aggregation for counts
export async function getWorkspaceStats(workspaceId: string) {
  const [contentCount, leadCount, campaignCount] = await db.$transaction([
    db.content.count({ where: { workspaceId } }),
    db.lead.count({ where: { workspaceId } }),
    db.emailCampaign.count({ where: { workspaceId } }),
  ]);

  return { contentCount, leadCount, campaignCount };
}

// Use cursor pagination for large datasets
export async function getLeadsPaginated(
  workspaceId: string,
  cursor?: string
) {
  const pageSize = 50;

  const leads = await db.lead.findMany({
    where: { workspaceId },
    take: pageSize + 1,
    ...(cursor && {
      cursor: { id: cursor },
      skip: 1,
    }),
    orderBy: { createdAt: 'desc' },
  });

  const hasMore = leads.length > pageSize;
  const items = hasMore ? leads.slice(0, -1) : leads;

  return {
    items,
    nextCursor: hasMore ? items[items.length - 1].id : null,
  };
}
```

## Testing Strategy

### Unit Tests

```typescript
// __tests__/services/content.test.ts
import { describe, it, expect, jest } from '@jest/globals';
import { generateContent } from '@/services/ai';

describe('Content Generation Service', () => {
  it('should generate TikTok content', async () => {
    const result = await generateContent({
      platform: 'tiktok',
      product: 'Infinity Cards',
      contentType: 'demo',
      tone: 'casual',
      length: 'short',
    });

    expect(result).toHaveProperty('title');
    expect(result).toHaveProperty('body');
    expect(result.body.length).toBeLessThan(200);
  });

  it('should handle generation errors gracefully', async () => {
    jest.spyOn(global, 'fetch').mockRejectedValue(new Error('API Error'));

    await expect(
      generateContent({ platform: 'tiktok', product: 'test' })
    ).rejects.toThrow('Content generation failed');
  });
});
```

### Integration Tests

```typescript
// __tests__/api/content.test.ts
import { createMockTRPCContext } from '@/test/utils';
import { appRouter } from '@/server/api/root';

describe('Content API', () => {
  it('should create content', async () => {
    const ctx = createMockTRPCContext({
      user: { id: 'user-1', workspaceId: 'ws-1' },
    });

    const caller = appRouter.createCaller(ctx);

    const content = await caller.content.create({
      workspaceId: 'ws-1',
      type: 'tiktok',
      title: 'Test Content',
      body: 'Test body',
    });

    expect(content.id).toBeDefined();
    expect(content.title).toBe('Test Content');
  });
});
```

### E2E Tests

```typescript
// e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/sign-in');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
  });

  test('should display metrics', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Dashboard');
    await expect(page.locator('[data-testid="revenue-metric"]')).toBeVisible();
    await expect(page.locator('[data-testid="traffic-metric"]')).toBeVisible();
  });

  test('should navigate to content section', async ({ page }) => {
    await page.click('a[href="/content"]');
    await page.waitForURL('/content');
    await expect(page.locator('h1')).toContainText('Content Hub');
  });

  test('should create new content', async ({ page }) => {
    await page.goto('/content');
    await page.click('button:has-text("Create Content")');

    await page.fill('[name="title"]', 'E2E Test Content');
    await page.fill('[name="body"]', 'Test content body');
    await page.click('button:has-text("Save")');

    await expect(page.locator('text=Content created successfully')).toBeVisible();
  });
});
```

## Deployment Configuration

### Docker Setup

```dockerfile
# Dockerfile
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm i --frozen-lockfile

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Generate Prisma client
RUN npx prisma generate

# Build application
RUN pnpm build

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/dashboard
      - REDIS_URL=redis://redis:6379
      - CLERK_SECRET_KEY=${CLERK_SECRET_KEY}
      - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - uploads:/app/uploads

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dashboard
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  worker:
    build: .
    command: node workers/index.js
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/dashboard
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
  uploads:
```

### Environment Variables

```bash
# .env.production
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dashboard

# Redis
REDIS_URL=redis://localhost:6379

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_xxxxx
CLERK_SECRET_KEY=sk_live_xxxxx
CLERK_WEBHOOK_SECRET=whsec_xxxxx

# API Keys
OPENAI_API_KEY=sk-xxxxx
TIKTOK_CLIENT_KEY=xxxxx
TIKTOK_CLIENT_SECRET=xxxxx
GOOGLE_CLIENT_ID=xxxxx
GOOGLE_CLIENT_SECRET=xxxxx
AMAZON_SP_CLIENT_ID=xxxxx
AMAZON_SP_CLIENT_SECRET=xxxxx

# Storage
AWS_ACCESS_KEY_ID=xxxxx
AWS_SECRET_ACCESS_KEY=xxxxx
AWS_S3_BUCKET=dashboard-uploads
AWS_S3_REGION=us-east-1

# Monitoring
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
NEXT_PUBLIC_VERCEL_ANALYTICS_ID=xxxxx

# Feature Flags
ENABLE_TIKTOK_INTEGRATION=true
ENABLE_EMAIL_MARKETING=true
ENABLE_BLOG_ENGINE=true
ENABLE_ANALYTICS=true
```

## Monitoring & Observability

### Sentry Configuration

```typescript
// sentry.client.config.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  debug: false,
  replaysOnErrorSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,

  integrations: [
    new Sentry.Replay({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],

  beforeSend(event, hint) {
    // Filter sensitive data
    if (event.request) {
      delete event.request.cookies;
      delete event.request.headers;
    }
    return event;
  },
});
```

### Performance Monitoring

```typescript
// lib/monitoring/performance.ts
export function measurePerformance(name: string) {
  const start = performance.now();

  return {
    end: () => {
      const duration = performance.now() - start;

      // Log to analytics
      if (typeof window !== 'undefined') {
        window.gtag?.('event', 'timing_complete', {
          name,
          value: Math.round(duration),
        });
      }

      // Log to console in dev
      if (process.env.NODE_ENV === 'development') {
        console.log(`${name}: ${duration.toFixed(2)}ms`);
      }

      return duration;
    },
  };
}

// Usage
export async function fetchDashboardData() {
  const perf = measurePerformance('dashboard_load');

  try {
    const data = await api.dashboard.overview();
    return data;
  } finally {
    perf.end();
  }
}
```

## Security Best Practices

### Input Validation

```typescript
// lib/validation/schemas.ts
import { z } from 'zod';

export const contentSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(500, 'Title too long')
    .regex(/^[^<>]*$/, 'Invalid characters in title'),

  body: z
    .string()
    .min(1, 'Content is required')
    .max(10000, 'Content too long')
    .transform((val) => sanitizeHtml(val)),

  type: z.enum(['tiktok', 'blog', 'email']),

  scheduledAt: z
    .date()
    .min(new Date(), 'Cannot schedule in the past')
    .optional(),
});

export const emailSchema = z.object({
  to: z.string().email('Invalid email address'),

  subject: z
    .string()
    .min(1, 'Subject is required')
    .max(200, 'Subject too long'),

  html: z
    .string()
    .transform((val) => sanitizeHtml(val, {
      allowedTags: ['p', 'br', 'strong', 'em', 'a', 'ul', 'li'],
      allowedAttributes: { a: ['href'] },
    })),
});
```

### Rate Limiting

```typescript
// middleware/rateLimit.ts
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(100, '1 m'),
  analytics: true,
});

export async function rateLimitMiddleware(req: Request) {
  const ip = req.headers.get('x-forwarded-for') ?? 'anonymous';
  const { success, limit, reset, remaining } = await ratelimit.limit(ip);

  if (!success) {
    return new Response('Too Many Requests', {
      status: 429,
      headers: {
        'X-RateLimit-Limit': limit.toString(),
        'X-RateLimit-Remaining': remaining.toString(),
        'X-RateLimit-Reset': new Date(reset).toISOString(),
      },
    });
  }

  return null;
}
```

### CSRF Protection

```typescript
// lib/security/csrf.ts
import { randomBytes } from 'crypto';

export function generateCSRFToken(): string {
  return randomBytes(32).toString('hex');
}

export function validateCSRFToken(
  token: string | null,
  sessionToken: string | null
): boolean {
  if (!token || !sessionToken) return false;
  return token === sessionToken;
}

// Usage in API route
export async function POST(req: Request) {
  const token = req.headers.get('x-csrf-token');
  const sessionToken = await getSession().then(s => s?.csrfToken);

  if (!validateCSRFToken(token, sessionToken)) {
    return new Response('Invalid CSRF token', { status: 403 });
  }

  // Process request
}
```

## Conclusion

This technical architecture provides a solid foundation for building the Organic Marketing Dashboard. The modular design allows for progressive enhancement as new features are added, while the robust infrastructure ensures scalability and reliability for both internal use and future service offerings.

Key architectural decisions:
- **Next.js App Router** for modern React features and optimal performance
- **tRPC** for type-safe API communication
- **Clerk** for unified authentication across services
- **PostgreSQL + Prisma** for reliable data persistence
- **Redis + BullMQ** for caching and background jobs
- **SSE** for real-time updates without WebSocket complexity

The architecture supports the roadmap's progressive enhancement approach, enabling quick MVP delivery in Phase 1 while maintaining flexibility for advanced features in later phases.