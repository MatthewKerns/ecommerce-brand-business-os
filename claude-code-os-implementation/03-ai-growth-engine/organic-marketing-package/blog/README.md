# Infinity Cards Blog

SEO-optimized blog platform for infinitycards.com, built with Next.js 14, TypeScript, and Tailwind CSS.

## Overview

This blog platform is designed to drive organic traffic through high-quality content about trading card games, tournament preparation, and collection management. It integrates with the BlogAgent for AI-powered content generation and uses MDX for content management.

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Content**: MDX (Markdown with JSX)
- **Deployment**: Vercel (recommended)

## Features

- 🚀 **Performance**: Optimized for Core Web Vitals, sub-3s page loads
- 📱 **Mobile-First**: Fully responsive design
- 🔍 **SEO**: Meta tags, structured data, sitemaps, robots.txt
- 📝 **MDX Content**: File-based content management with React components
- 🎨 **Brand Consistency**: Follows Infinity Cards design system
- 📊 **Analytics**: Google Analytics 4 integration

## Getting Started

### Prerequisites

- Node.js 20+ and npm
- Copy `.env.local.example` to `.env.local` and configure

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Visit [http://localhost:3001](http://localhost:3001)

### Production Build

```bash
npm run build
npm start
```

## Project Structure

```
blog/
├── app/                    # Next.js App Router
│   ├── blog/              # Blog routes
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/            # React components
├── content/              # MDX blog posts
├── lib/                  # Utilities and helpers
│   ├── cms.ts           # Content management functions
│   ├── seo.ts           # SEO utilities
│   └── types.ts         # TypeScript types
└── public/              # Static assets
```

## Content Management

Blog posts are written in MDX format and stored in the `content/` directory. Each post includes:

- Frontmatter metadata (title, description, date, author, tags)
- Markdown content with embedded React components
- Automatic SEO optimization

### Creating a New Post

1. Create a new `.mdx` file in `content/blog/`
2. Add frontmatter metadata
3. Write your content
4. Commit and deploy

See `CONTENT_WORKFLOW.md` for detailed publishing workflow.

## SEO Features

- Dynamic meta tags and Open Graph tags
- JSON-LD structured data (Article schema)
- Automatic sitemap generation
- Optimized images with lazy loading
- Mobile-responsive design
- Fast page loads (< 3s target)

## Deployment

Deploy to Vercel with one click or configure custom hosting.

See `DEPLOYMENT.md` for detailed deployment instructions.

## Integration with BlogAgent

This blog platform is designed to work seamlessly with the BlogAgent content generation system:

1. BlogAgent generates blog posts based on trending topics
2. Posts are saved as MDX files in the `content/` directory
3. Blog automatically indexes and displays new content
4. SEO optimization is applied automatically

## Scripts

- `npm run dev` - Start development server (port 3001)
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting

## Performance Targets

- **Mobile PageSpeed Score**: > 80
- **Desktop PageSpeed Score**: > 90
- **Page Load Time**: < 3 seconds
- **Core Web Vitals**: All passing
  - LCP (Largest Contentful Paint): < 2.5s
  - FID (First Input Delay): < 100ms
  - CLS (Cumulative Layout Shift): < 0.1

## License

Private - Infinity Cards

## Support

For questions or issues, contact the development team.
