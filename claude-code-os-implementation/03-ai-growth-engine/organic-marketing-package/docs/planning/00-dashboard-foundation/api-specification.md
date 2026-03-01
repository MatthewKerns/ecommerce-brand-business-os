# Dashboard API Specification

## Overview

This document provides comprehensive API documentation for the Organic Marketing Dashboard. The API uses tRPC for type-safe communication with REST fallbacks for external integrations.

## API Architecture

### Base Configuration

```yaml
Protocol: HTTPS
Base URL: https://api.dashboard.infinitycards.com
Version: v1
Format: JSON
Authentication: Bearer Token (Clerk JWT)
Rate Limiting: 100 requests per minute per user
```

### Response Format

#### Success Response
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2024-03-01T10:00:00Z",
    "version": "1.0.0",
    "requestId": "req_abc123"
  }
}
```

#### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { ... }
  },
  "meta": {
    "timestamp": "2024-03-01T10:00:00Z",
    "requestId": "req_abc123"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Invalid input data |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |

## Authentication Endpoints

### Sign In
```http
POST /api/auth/signin
```

Request:
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "token": "jwt_token_here",
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "name": "John Doe",
      "workspaces": [
        {
          "id": "ws_123",
          "name": "Infinity Cards",
          "role": "owner"
        }
      ]
    }
  }
}
```

### Sign Out
```http
POST /api/auth/signout
Authorization: Bearer {token}
```

Response:
```json
{
  "success": true,
  "data": {
    "message": "Successfully signed out"
  }
}
```

### Refresh Token
```http
POST /api/auth/refresh
Authorization: Bearer {refresh_token}
```

Response:
```json
{
  "success": true,
  "data": {
    "token": "new_jwt_token",
    "expiresAt": "2024-03-01T12:00:00Z"
  }
}
```

### Get Current User
```http
GET /api/auth/me
Authorization: Bearer {token}
```

Response:
```json
{
  "success": true,
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "avatarUrl": "https://...",
    "currentWorkspace": {
      "id": "ws_123",
      "name": "Infinity Cards",
      "role": "owner"
    }
  }
}
```

## Workspace Endpoints

### List Workspaces
```http
GET /api/workspaces
Authorization: Bearer {token}
```

Response:
```json
{
  "success": true,
  "data": {
    "workspaces": [
      {
        "id": "ws_123",
        "name": "Infinity Cards",
        "slug": "infinity-cards",
        "logoUrl": "https://...",
        "role": "owner",
        "memberCount": 5,
        "subscription": "pro"
      }
    ]
  }
}
```

### Create Workspace
```http
POST /api/workspaces
Authorization: Bearer {token}
```

Request:
```json
{
  "name": "New Brand",
  "slug": "new-brand"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "workspace": {
      "id": "ws_456",
      "name": "New Brand",
      "slug": "new-brand",
      "ownerId": "user_123",
      "createdAt": "2024-03-01T10:00:00Z"
    }
  }
}
```

### Update Workspace
```http
PUT /api/workspaces/{workspaceId}
Authorization: Bearer {token}
```

Request:
```json
{
  "name": "Updated Brand Name",
  "logoUrl": "https://...",
  "settings": {
    "timezone": "America/New_York",
    "currency": "USD"
  }
}
```

Response:
```json
{
  "success": true,
  "data": {
    "workspace": {
      "id": "ws_123",
      "name": "Updated Brand Name",
      "updatedAt": "2024-03-01T10:00:00Z"
    }
  }
}
```

### Switch Workspace
```http
POST /api/workspaces/{workspaceId}/switch
Authorization: Bearer {token}
```

Response:
```json
{
  "success": true,
  "data": {
    "workspace": {
      "id": "ws_123",
      "name": "Infinity Cards"
    },
    "token": "new_session_token"
  }
}
```

### Invite Member
```http
POST /api/workspaces/{workspaceId}/invite
Authorization: Bearer {token}
```

Request:
```json
{
  "email": "newmember@example.com",
  "role": "member"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "invitation": {
      "id": "inv_123",
      "email": "newmember@example.com",
      "role": "member",
      "expiresAt": "2024-03-08T10:00:00Z"
    }
  }
}
```

## Dashboard Endpoints

### Get Overview
```http
GET /api/dashboard/overview
Authorization: Bearer {token}
```

Query Parameters:
- `workspaceId` (required): Workspace ID
- `dateRange`: Period (`today`, `week`, `month`, `quarter`, `year`)

Response:
```json
{
  "success": true,
  "data": {
    "metrics": {
      "revenue": {
        "value": 12450,
        "change": 23.5,
        "trend": "up"
      },
      "traffic": {
        "value": 45200,
        "change": 15.2,
        "trend": "up"
      },
      "leads": {
        "value": 892,
        "change": 34.1,
        "trend": "up"
      },
      "conversion": {
        "value": 3.2,
        "change": 0.5,
        "trend": "up"
      }
    },
    "channels": [
      {
        "name": "TikTok",
        "revenue": 5600,
        "traffic": 20340,
        "percentage": 45
      },
      {
        "name": "Blog",
        "revenue": 3735,
        "traffic": 13560,
        "percentage": 30
      },
      {
        "name": "Email",
        "revenue": 3115,
        "traffic": 11300,
        "percentage": 25
      }
    ],
    "systemHealth": {
      "status": "healthy",
      "services": {
        "tiktok": "operational",
        "email": "operational",
        "blog": "operational",
        "mcf": "operational"
      }
    },
    "recentActivity": [
      {
        "id": "act_123",
        "type": "content_published",
        "title": "New TikTok video scheduled",
        "timestamp": "2024-03-01T09:45:00Z"
      }
    ]
  }
}
```

### Get Metrics
```http
GET /api/dashboard/metrics
Authorization: Bearer {token}
```

Query Parameters:
- `workspaceId` (required): Workspace ID
- `metrics[]`: Array of metric names
- `startDate`: ISO date string
- `endDate`: ISO date string
- `granularity`: `hour`, `day`, `week`, `month`

Response:
```json
{
  "success": true,
  "data": {
    "metrics": {
      "revenue": {
        "total": 45000,
        "series": [
          { "date": "2024-03-01", "value": 1500 },
          { "date": "2024-03-02", "value": 1650 }
        ]
      },
      "traffic": {
        "total": 125000,
        "series": [
          { "date": "2024-03-01", "value": 4200 },
          { "date": "2024-03-02", "value": 4500 }
        ]
      }
    }
  }
}
```

### Get Activity Feed
```http
GET /api/dashboard/activity
Authorization: Bearer {token}
```

Query Parameters:
- `workspaceId` (required): Workspace ID
- `limit`: Number of items (default: 20)
- `offset`: Pagination offset
- `types[]`: Filter by activity types

Response:
```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": "act_123",
        "type": "content_published",
        "title": "TikTok video published",
        "description": "Product unboxing video went live",
        "user": {
          "id": "user_123",
          "name": "John Doe",
          "avatarUrl": "https://..."
        },
        "metadata": {
          "contentId": "cnt_456",
          "platform": "tiktok"
        },
        "timestamp": "2024-03-01T10:00:00Z"
      }
    ],
    "pagination": {
      "total": 156,
      "limit": 20,
      "offset": 0,
      "hasMore": true
    }
  }
}
```

## Content Management Endpoints

### List Content
```http
GET /api/content
Authorization: Bearer {token}
```

Query Parameters:
- `workspaceId` (required): Workspace ID
- `type`: Filter by type (`tiktok`, `blog`, `email`)
- `status`: Filter by status (`draft`, `scheduled`, `published`)
- `search`: Search in title and body
- `limit`: Items per page (default: 20)
- `offset`: Pagination offset

Response:
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "id": "cnt_123",
        "type": "tiktok",
        "status": "scheduled",
        "title": "Product Demo: Infinity Cards",
        "body": "Check out our amazing card game...",
        "mediaUrls": [
          "https://..."
        ],
        "scheduledAt": "2024-03-05T15:00:00Z",
        "metrics": {
          "views": 1250,
          "likes": 89,
          "shares": 12
        },
        "createdBy": {
          "id": "user_123",
          "name": "John Doe"
        },
        "createdAt": "2024-03-01T10:00:00Z"
      }
    ],
    "pagination": {
      "total": 45,
      "limit": 20,
      "offset": 0
    }
  }
}
```

### Get Content
```http
GET /api/content/{contentId}
Authorization: Bearer {token}
```

Response:
```json
{
  "success": true,
  "data": {
    "content": {
      "id": "cnt_123",
      "type": "tiktok",
      "status": "published",
      "title": "Product Demo: Infinity Cards",
      "body": "Full content text...",
      "mediaUrls": ["https://..."],
      "metadata": {
        "duration": 30,
        "hashtags": ["#cardgame", "#tabletop"],
        "mentions": ["@partner"]
      },
      "scheduledAt": null,
      "publishedAt": "2024-03-01T15:00:00Z",
      "metrics": {
        "views": 5420,
        "likes": 234,
        "shares": 45,
        "saves": 89,
        "clicks": 120,
        "conversions": 5,
        "revenue": 149.95
      },
      "createdBy": {
        "id": "user_123",
        "name": "John Doe",
        "avatarUrl": "https://..."
      },
      "createdAt": "2024-02-28T10:00:00Z",
      "updatedAt": "2024-03-01T14:55:00Z"
    }
  }
}
```

### Create Content
```http
POST /api/content
Authorization: Bearer {token}
```

Request:
```json
{
  "workspaceId": "ws_123",
  "type": "tiktok",
  "title": "New Product Launch",
  "body": "Exciting new product...",
  "mediaUrls": ["https://..."],
  "scheduledAt": "2024-03-10T15:00:00Z",
  "metadata": {
    "hashtags": ["#newproduct", "#launch"],
    "productId": "prod_456"
  }
}
```

Response:
```json
{
  "success": true,
  "data": {
    "content": {
      "id": "cnt_789",
      "status": "scheduled",
      "createdAt": "2024-03-01T10:00:00Z"
    }
  }
}
```

### Update Content
```http
PUT /api/content/{contentId}
Authorization: Bearer {token}
```

Request:
```json
{
  "title": "Updated Title",
  "body": "Updated content...",
  "scheduledAt": "2024-03-12T15:00:00Z"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "content": {
      "id": "cnt_123",
      "updatedAt": "2024-03-01T10:00:00Z"
    }
  }
}
```

### Delete Content
```http
DELETE /api/content/{contentId}
Authorization: Bearer {token}
```

Response:
```json
{
  "success": true,
  "data": {
    "message": "Content deleted successfully"
  }
}
```

### Generate Content
```http
POST /api/content/generate
Authorization: Bearer {token}
```

Request:
```json
{
  "workspaceId": "ws_123",
  "platform": "tiktok",
  "product": "Infinity Cards",
  "contentType": "demo",
  "tone": "casual",
  "length": "short",
  "context": "Focus on the unique gameplay mechanics"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "jobId": "job_123",
    "status": "processing",
    "estimatedTime": 10
  }
}
```

### Check Generation Status
```http
GET /api/content/generate/{jobId}
Authorization: Bearer {token}
```

Response (Processing):
```json
{
  "success": true,
  "data": {
    "jobId": "job_123",
    "status": "processing",
    "progress": 65
  }
}
```

Response (Complete):
```json
{
  "success": true,
  "data": {
    "jobId": "job_123",
    "status": "complete",
    "content": {
      "title": "Generated Title",
      "body": "Generated content...",
      "metadata": {
        "aiGenerated": true,
        "model": "gpt-4"
      }
    }
  }
}
```

### Get Content Calendar
```http
GET /api/content/calendar
Authorization: Bearer {token}
```

Query Parameters:
- `workspaceId` (required): Workspace ID
- `startDate`: ISO date string
- `endDate`: ISO date string
- `types[]`: Filter by content types

Response:
```json
{
  "success": true,
  "data": {
    "calendar": {
      "2024-03-01": [
        {
          "id": "cnt_123",
          "type": "tiktok",
          "title": "Morning Post",
          "time": "09:00:00",
          "status": "published"
        }
      ],
      "2024-03-02": [
        {
          "id": "cnt_456",
          "type": "blog",
          "title": "Weekly Roundup",
          "time": "10:00:00",
          "status": "scheduled"
        }
      ]
    }
  }
}
```

## Email Marketing Endpoints

### List Campaigns
```http
GET /api/email/campaigns
Authorization: Bearer {token}
```

Query Parameters:
- `workspaceId` (required): Workspace ID
- `type`: Filter by type (`one-time`, `sequence`, `triggered`)
- `status`: Filter by status (`draft`, `scheduled`, `active`, `paused`, `completed`)
- `limit`: Items per page
- `offset`: Pagination offset

Response:
```json
{
  "success": true,
  "data": {
    "campaigns": [
      {
        "id": "camp_123",
        "name": "Welcome Series",
        "type": "sequence",
        "status": "active",
        "recipientCount": 450,
        "metrics": {
          "sent": 1250,
          "opened": 562,
          "clicked": 89,
          "converted": 12
        },
        "createdAt": "2024-02-15T10:00:00Z"
      }
    ],
    "pagination": {
      "total": 12,
      "limit": 20,
      "offset": 0
    }
  }
}
```

### Create Campaign
```http
POST /api/email/campaigns
Authorization: Bearer {token}
```

Request:
```json
{
  "workspaceId": "ws_123",
  "name": "Spring Sale Campaign",
  "type": "one-time",
  "segment": {
    "criteria": [
      {
        "field": "tags",
        "operator": "contains",
        "value": "customer"
      }
    ]
  },
  "content": {
    "subject": "Exclusive Spring Sale",
    "preheader": "Save 20% this weekend",
    "html": "<html>...</html>",
    "text": "Plain text version..."
  },
  "schedule": {
    "sendAt": "2024-03-15T10:00:00Z"
  }
}
```

Response:
```json
{
  "success": true,
  "data": {
    "campaign": {
      "id": "camp_456",
      "status": "scheduled",
      "recipientCount": 892,
      "createdAt": "2024-03-01T10:00:00Z"
    }
  }
}
```

### Get Email Sequences
```http
GET /api/email/sequences
Authorization: Bearer {token}
```

Query Parameters:
- `workspaceId` (required): Workspace ID
- `status`: Filter by status

Response:
```json
{
  "success": true,
  "data": {
    "sequences": [
      {
        "id": "seq_123",
        "name": "Welcome Series",
        "status": "active",
        "steps": [
          {
            "id": "step_1",
            "name": "Welcome Email",
            "delay": 0,
            "subject": "Welcome to Infinity Cards"
          },
          {
            "id": "step_2",
            "name": "Product Tips",
            "delay": 259200,
            "subject": "3 Tips to Master Infinity Cards"
          }
        ],
        "metrics": {
          "enrolled": 450,
          "completed": 234,
          "converted": 45
        }
      }
    ]
  }
}
```

### Create Email Sequence
```http
POST /api/email/sequences
Authorization: Bearer {token}
```

Request:
```json
{
  "workspaceId": "ws_123",
  "name": "Onboarding Flow",
  "trigger": {
    "type": "tag_added",
    "value": "new_customer"
  },
  "steps": [
    {
      "name": "Welcome",
      "delay": 0,
      "content": {
        "subject": "Welcome!",
        "html": "<html>...</html>"
      }
    },
    {
      "name": "First Tips",
      "delay": 86400,
      "content": {
        "subject": "Getting Started",
        "html": "<html>...</html>"
      },
      "condition": {
        "type": "email_opened",
        "stepId": "step_1"
      }
    }
  ]
}
```

Response:
```json
{
  "success": true,
  "data": {
    "sequence": {
      "id": "seq_456",
      "status": "active",
      "createdAt": "2024-03-01T10:00:00Z"
    }
  }
}
```

### List Leads
```http
GET /api/email/leads
Authorization: Bearer {token}
```

Query Parameters:
- `workspaceId` (required): Workspace ID
- `status`: Filter by status (`active`, `unsubscribed`, `bounced`)
- `tags[]`: Filter by tags
- `search`: Search by email or name
- `limit`: Items per page
- `cursor`: Cursor for pagination

Response:
```json
{
  "success": true,
  "data": {
    "leads": [
      {
        "id": "lead_123",
        "email": "john@example.com",
        "name": "John Doe",
        "tags": ["customer", "vip"],
        "source": "website",
        "status": "active",
        "customFields": {
          "company": "Acme Corp",
          "purchaseCount": 5
        },
        "stats": {
          "emailsSent": 12,
          "emailsOpened": 8,
          "linksClicked": 3
        },
        "createdAt": "2024-01-15T10:00:00Z"
      }
    ],
    "pagination": {
      "nextCursor": "cursor_xyz",
      "hasMore": true
    }
  }
}
```

### Import Leads
```http
POST /api/email/leads/import
Authorization: Bearer {token}
```

Request:
```json
{
  "workspaceId": "ws_123",
  "source": "csv_upload",
  "mapping": {
    "email": "Email Address",
    "name": "Full Name",
    "customFields": {
      "company": "Company Name"
    }
  },
  "data": [
    {
      "Email Address": "new@example.com",
      "Full Name": "New Lead",
      "Company Name": "New Corp"
    }
  ],
  "tags": ["imported", "march-2024"]
}
```

Response:
```json
{
  "success": true,
  "data": {
    "imported": 145,
    "skipped": 5,
    "errors": [
      {
        "row": 3,
        "error": "Invalid email format"
      }
    ]
  }
}
```

## Analytics Endpoints

### Get Channel Performance
```http
GET /api/analytics/channels
Authorization: Bearer {token}
```

Query Parameters:
- `workspaceId` (required): Workspace ID
- `channels[]`: Filter by channels
- `metrics[]`: Metrics to include
- `startDate`: ISO date string
- `endDate`: ISO date string
- `granularity`: `hour`, `day`, `week`, `month`

Response:
```json
{
  "success": true,
  "data": {
    "channels": {
      "tiktok": {
        "metrics": {
          "revenue": 5600,
          "traffic": 20340,
          "conversions": 89,
          "avgOrderValue": 62.92
        },
        "series": [
          {
            "date": "2024-03-01",
            "revenue": 450,
            "traffic": 1520
          }
        ]
      },
      "blog": {
        "metrics": {
          "revenue": 3735,
          "traffic": 13560,
          "conversions": 45,
          "avgOrderValue": 83.00
        },
        "series": [
          {
            "date": "2024-03-01",
            "revenue": 250,
            "traffic": 890
          }
        ]
      }
    }
  }
}
```

### Get Funnel Analysis
```http
GET /api/analytics/funnel
Authorization: Bearer {token}
```

Query Parameters:
- `workspaceId` (required): Workspace ID
- `startDate`: ISO date string
- `endDate`: ISO date string

Response:
```json
{
  "success": true,
  "data": {
    "funnel": {
      "steps": [
        {
          "name": "Visit",
          "count": 45200,
          "percentage": 100
        },
        {
          "name": "View Product",
          "count": 12500,
          "percentage": 27.7,
          "dropoff": 72.3
        },
        {
          "name": "Add to Cart",
          "count": 3200,
          "percentage": 7.1,
          "dropoff": 74.4
        },
        {
          "name": "Checkout",
          "count": 1850,
          "percentage": 4.1,
          "dropoff": 42.2
        },
        {
          "name": "Purchase",
          "count": 892,
          "percentage": 2.0,
          "dropoff": 51.8
        }
      ],
      "overallConversion": 2.0
    }
  }
}
```

### Get Attribution Report
```http
GET /api/analytics/attribution
Authorization: Bearer {token}
```

Query Parameters:
- `workspaceId` (required): Workspace ID
- `model`: Attribution model (`first`, `last`, `linear`, `time-decay`)
- `startDate`: ISO date string
- `endDate`: ISO date string

Response:
```json
{
  "success": true,
  "data": {
    "attribution": {
      "model": "linear",
      "channels": [
        {
          "channel": "tiktok",
          "touchpoints": 2450,
          "attributedRevenue": 8900,
          "attributedConversions": 145,
          "weight": 0.42
        },
        {
          "channel": "email",
          "touchpoints": 1890,
          "attributedRevenue": 6700,
          "attributedConversions": 89,
          "weight": 0.32
        },
        {
          "channel": "blog",
          "touchpoints": 1200,
          "attributedRevenue": 5400,
          "attributedConversions": 67,
          "weight": 0.26
        }
      ],
      "totalRevenue": 21000,
      "totalConversions": 301
    }
  }
}
```

### Create Custom Report
```http
POST /api/analytics/reports
Authorization: Bearer {token}
```

Request:
```json
{
  "workspaceId": "ws_123",
  "name": "Monthly Performance Report",
  "type": "custom",
  "config": {
    "metrics": ["revenue", "traffic", "conversion"],
    "dimensions": ["channel", "date"],
    "filters": {
      "channel": ["tiktok", "email"]
    },
    "dateRange": {
      "start": "2024-03-01",
      "end": "2024-03-31"
    }
  },
  "schedule": {
    "frequency": "weekly",
    "dayOfWeek": "monday",
    "time": "09:00",
    "recipients": ["team@example.com"]
  }
}
```

Response:
```json
{
  "success": true,
  "data": {
    "report": {
      "id": "rpt_123",
      "name": "Monthly Performance Report",
      "createdAt": "2024-03-01T10:00:00Z"
    }
  }
}
```

### Export Analytics
```http
POST /api/analytics/export
Authorization: Bearer {token}
```

Request:
```json
{
  "workspaceId": "ws_123",
  "format": "csv",
  "data": "channel_performance",
  "dateRange": {
    "start": "2024-03-01",
    "end": "2024-03-31"
  }
}
```

Response:
```json
{
  "success": true,
  "data": {
    "exportId": "exp_123",
    "status": "processing",
    "estimatedTime": 30
  }
}
```

### Get Export Status
```http
GET /api/analytics/export/{exportId}
Authorization: Bearer {token}
```

Response (Complete):
```json
{
  "success": true,
  "data": {
    "exportId": "exp_123",
    "status": "complete",
    "downloadUrl": "https://cdn.example.com/exports/exp_123.csv",
    "expiresAt": "2024-03-08T10:00:00Z"
  }
}
```

## Integration Endpoints

### List Integrations
```http
GET /api/integrations
Authorization: Bearer {token}
```

Query Parameters:
- `workspaceId` (required): Workspace ID

Response:
```json
{
  "success": true,
  "data": {
    "integrations": [
      {
        "id": "int_tiktok",
        "name": "TikTok",
        "status": "connected",
        "config": {
          "accounts": [
            {
              "id": "tt_123",
              "username": "@infinitycards",
              "followers": 12500
            }
          ]
        },
        "lastSync": "2024-03-01T09:00:00Z"
      },
      {
        "id": "int_gmail",
        "name": "Gmail",
        "status": "connected",
        "config": {
          "email": "marketing@infinitycards.com"
        },
        "lastSync": "2024-03-01T09:30:00Z"
      },
      {
        "id": "int_mcf",
        "name": "Amazon MCF",
        "status": "disconnected",
        "config": null,
        "lastSync": null
      }
    ]
  }
}
```

### Connect Integration
```http
POST /api/integrations/{integrationId}/connect
Authorization: Bearer {token}
```

Request (TikTok):
```json
{
  "workspaceId": "ws_123",
  "config": {
    "clientKey": "xxx",
    "clientSecret": "xxx",
    "redirectUri": "https://dashboard.infinitycards.com/integrations/tiktok/callback"
  }
}
```

Response:
```json
{
  "success": true,
  "data": {
    "authUrl": "https://www.tiktok.com/auth/authorize?...",
    "state": "state_123"
  }
}
```

### Disconnect Integration
```http
POST /api/integrations/{integrationId}/disconnect
Authorization: Bearer {token}
```

Request:
```json
{
  "workspaceId": "ws_123"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "message": "Integration disconnected successfully"
  }
}
```

### Sync Integration
```http
POST /api/integrations/{integrationId}/sync
Authorization: Bearer {token}
```

Request:
```json
{
  "workspaceId": "ws_123",
  "full": false
}
```

Response:
```json
{
  "success": true,
  "data": {
    "jobId": "sync_123",
    "status": "processing"
  }
}
```

### Test Integration
```http
POST /api/integrations/{integrationId}/test
Authorization: Bearer {token}
```

Request:
```json
{
  "workspaceId": "ws_123"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "status": "success",
    "latency": 245,
    "details": {
      "connection": "ok",
      "authentication": "ok",
      "permissions": "ok"
    }
  }
}
```

## Webhook Endpoints

### Register Webhook
```http
POST /api/webhooks
Authorization: Bearer {token}
```

Request:
```json
{
  "workspaceId": "ws_123",
  "url": "https://example.com/webhook",
  "events": ["content.published", "email.sent", "lead.created"],
  "secret": "webhook_secret_key"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "webhook": {
      "id": "wh_123",
      "url": "https://example.com/webhook",
      "events": ["content.published", "email.sent", "lead.created"],
      "status": "active",
      "createdAt": "2024-03-01T10:00:00Z"
    }
  }
}
```

### List Webhooks
```http
GET /api/webhooks
Authorization: Bearer {token}
```

Query Parameters:
- `workspaceId` (required): Workspace ID

Response:
```json
{
  "success": true,
  "data": {
    "webhooks": [
      {
        "id": "wh_123",
        "url": "https://example.com/webhook",
        "events": ["content.published"],
        "status": "active",
        "lastTriggered": "2024-03-01T09:00:00Z",
        "failureCount": 0
      }
    ]
  }
}
```

### Delete Webhook
```http
DELETE /api/webhooks/{webhookId}
Authorization: Bearer {token}
```

Response:
```json
{
  "success": true,
  "data": {
    "message": "Webhook deleted successfully"
  }
}
```

## Webhook Events

### Event Format
```json
{
  "id": "evt_123",
  "type": "content.published",
  "workspaceId": "ws_123",
  "data": { ... },
  "timestamp": "2024-03-01T10:00:00Z"
}
```

### Event Types

| Event | Description | Data |
|-------|-------------|------|
| `content.published` | Content was published | Content object |
| `content.failed` | Content publishing failed | Error details |
| `email.sent` | Email was sent | Campaign/email details |
| `email.bounced` | Email bounced | Bounce details |
| `lead.created` | New lead added | Lead object |
| `lead.unsubscribed` | Lead unsubscribed | Lead ID |
| `integration.connected` | Integration connected | Integration details |
| `integration.failed` | Integration failed | Error details |

## Rate Limiting

### Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 2024-03-01T10:05:00Z
```

### Rate Limit Response
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests. Please retry after 2024-03-01T10:05:00Z",
    "retryAfter": "2024-03-01T10:05:00Z"
  }
}
```

### Rate Limits by Tier

| Tier | Requests/Minute | Burst Limit |
|------|----------------|-------------|
| Free | 60 | 10 |
| Pro | 300 | 50 |
| Enterprise | 1000 | 200 |

## API Versioning

### Version Header
```http
X-API-Version: 1.0.0
```

### Deprecation Notice
```http
X-API-Deprecation: true
X-API-Sunset: 2024-06-01T00:00:00Z
```

## Testing

### Test Environment
```yaml
Base URL: https://api-staging.dashboard.infinitycards.com
Authentication: Use test tokens from Clerk dashboard
Rate Limits: Same as production
Data Persistence: Cleared daily
```

### Test Credentials
```json
{
  "testUser": {
    "email": "test@infinitycards.com",
    "password": "test_password_123",
    "apiKey": "test_pk_xxx"
  }
}
```

## SDKs and Libraries

### JavaScript/TypeScript
```bash
npm install @infinitycards/dashboard-sdk
```

```typescript
import { DashboardClient } from '@infinitycards/dashboard-sdk';

const client = new DashboardClient({
  apiKey: 'your_api_key',
  workspace: 'ws_123'
});

// Get dashboard overview
const overview = await client.dashboard.getOverview();

// Create content
const content = await client.content.create({
  type: 'tiktok',
  title: 'New Video',
  body: 'Content...'
});
```

### Python
```bash
pip install infinitycards-dashboard
```

```python
from infinitycards_dashboard import DashboardClient

client = DashboardClient(
    api_key='your_api_key',
    workspace='ws_123'
)

# Get dashboard overview
overview = client.dashboard.get_overview()

# Create content
content = client.content.create(
    type='tiktok',
    title='New Video',
    body='Content...'
)
```

## Support

### Contact
- Email: api-support@infinitycards.com
- Discord: https://discord.gg/infinitycards
- Documentation: https://docs.infinitycards.com/api

### Status Page
https://status.infinitycards.com

### Changelog
https://docs.infinitycards.com/api/changelog