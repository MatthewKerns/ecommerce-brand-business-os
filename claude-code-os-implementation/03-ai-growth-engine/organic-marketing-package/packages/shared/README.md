# Shared

Shared types, utilities, and configuration used across multiple packages in the Organic Marketing platform.

## Contents

- **Types** - Common TypeScript type definitions shared between dashboard, mcf-connector, and blog
- **Config** - Shared configuration schemas and defaults
- **Utils** - Common utility functions

## Usage

Referenced by other packages via npm workspace linking:

```typescript
import { ContentMetrics } from '@organic-marketing/shared';
```

## Setup

```bash
cd packages/shared
npm install
npm run build
```
