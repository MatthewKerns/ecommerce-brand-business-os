# Content Publishing Workflow

This document outlines the complete workflow for creating, editing, and publishing blog content on the Infinity Cards blog platform.

## Overview

The Infinity Cards blog uses a file-based MDX content management system. Content flows through the following stages:

```
BlogAgent Generation → Import/Manual Creation → Preview → Publish → Verify Live
```

## Workflow Stages

### 1. Content Generation (BlogAgent)

The BlogAgent automatically generates blog content based on trending topics and SEO optimization.

**BlogAgent Output Location:**
```
content-agents/output/blog/
```

**Output Format:**
- Markdown (.md) files with frontmatter
- Auto-generated titles, descriptions, and tags
- SEO-optimized content structure

**Accessing BlogAgent:**
```bash
cd content-agents
source .venv/bin/activate
python -m agents.blog_agent
```

### 2. Content Import/Manual Creation

#### Option A: Import from BlogAgent

1. **Locate Generated Content:**
   ```bash
   ls content-agents/output/blog/
   ```

2. **Review Content:**
   - Check title, description, and tags
   - Verify content quality and accuracy
   - Ensure SEO optimization

3. **Import to Blog:**
   ```bash
   # Copy file to blog content directory
   cp content-agents/output/blog/[filename].md \
      blog/content/posts/[slug].mdx
   ```

4. **Update Frontmatter:**
   - Convert filename to appropriate slug
   - Verify all required fields
   - Add featured image path
   - Set `published: false` for drafts

#### Option B: Manual Content Creation

1. **Create New MDX File:**
   ```bash
   cd blog/content/posts/
   touch [slug].mdx
   ```

2. **Add Frontmatter and Content:**
   See "Required Content Fields" section below

### 3. Required Content Fields

Every blog post must include the following frontmatter fields:

```yaml
---
title: "Your Compelling Blog Post Title"
description: "A concise 150-160 character description for SEO and social sharing"
date: "2024-02-26"  # Format: YYYY-MM-DD
category: "tournament-prep"  # See categories below
tags: ["strategy", "competitive", "beginner"]  # 2-5 relevant tags
author: "InfinityCards Team"  # Default author name
image: "/images/blog/featured-image.jpg"  # Optional but recommended
published: true  # Set to false for drafts
---
```

#### Available Categories

- `tournament-prep` - Tournament preparation and competitive play
- `deck-building` - Deck construction and strategy
- `card-care` - Card protection, grading, and storage
- `strategy` - Game strategy and tactics
- `guides` - How-to guides and tutorials
- `news` - Industry news and updates

#### Content Guidelines

**Title:**
- 50-60 characters optimal
- Include primary keyword
- Compelling and click-worthy
- Avoid clickbait

**Description:**
- 150-160 characters
- Include target keywords naturally
- Summarize key value proposition
- Include call-to-action when appropriate

**Date:**
- Use current date for new posts
- Format: YYYY-MM-DD
- Will be displayed as human-readable format

**Tags:**
- Use 2-5 relevant tags
- Keep tags consistent across posts
- Common tags: strategy, beginner, advanced, competitive, casual, budget, premium

**Image:**
- Recommended size: 1200x630px (OG image ratio)
- Format: JPG or PNG
- Optimize file size (< 200KB)
- Store in `/public/images/blog/`

**Published Status:**
- `published: true` - Live on production
- `published: false` - Draft (not visible)

### 4. Content Structure

Use proper heading hierarchy for SEO and accessibility:

```markdown
# Main Title (H1) - Auto-generated from frontmatter

## Major Section (H2)
Content here...

### Subsection (H3)
Content here...

#### Minor Point (H4)
Content here...
```

**Best Practices:**
- Start with H2 for main sections (H1 is the title)
- Use H3 for subsections within H2
- Maintain logical hierarchy
- Use descriptive heading text

### 5. SEO Checklist

Before publishing, verify:

#### Content SEO
- [ ] Target keyword in title
- [ ] Target keyword in first paragraph
- [ ] Target keyword in at least one H2
- [ ] Internal links to other blog posts (2-3 minimum)
- [ ] External links to authoritative sources
- [ ] Alt text for all images
- [ ] 800+ words for long-form content
- [ ] Natural keyword density (1-2%)

#### Technical SEO
- [ ] Unique, descriptive title (50-60 chars)
- [ ] Compelling meta description (150-160 chars)
- [ ] Featured image included (1200x630px)
- [ ] Proper heading hierarchy (H2 → H3 → H4)
- [ ] No broken links
- [ ] Mobile-friendly content
- [ ] Fast-loading images (< 200KB)

#### User Experience
- [ ] Clear, scannable structure
- [ ] Short paragraphs (2-4 sentences)
- [ ] Bullet points for lists
- [ ] Relevant images/graphics
- [ ] Table of contents (auto-generated for 3+ H2s)
- [ ] Related posts (auto-populated)

### 6. Preview & Testing

#### Local Development Server

1. **Start Dev Server:**
   ```bash
   cd blog
   npm run dev
   ```
   Server runs on: `http://localhost:3001`

2. **Preview Your Post:**
   - **Blog Index:** `http://localhost:3001/blog`
   - **Individual Post:** `http://localhost:3001/blog/[slug]`
   - **Category Page:** `http://localhost:3001/blog/category/[category]`

3. **Check Rendering:**
   - Verify frontmatter displays correctly
   - Check all headings render properly
   - Test Table of Contents links
   - Verify images load
   - Test social share buttons
   - Check related posts appear

4. **Test Responsiveness:**
   - Mobile view (< 768px)
   - Tablet view (768px - 1024px)
   - Desktop view (> 1024px)

#### Content Quality Review

- [ ] No spelling or grammar errors
- [ ] All links work correctly
- [ ] Images display properly
- [ ] Code blocks (if any) have proper syntax highlighting
- [ ] Reading time is accurate
- [ ] Category and tags are correct
- [ ] No console errors in browser

### 7. Publishing Process

#### Mark as Published

1. **Update Frontmatter:**
   ```yaml
   published: true
   ```

2. **Verify Build:**
   ```bash
   npm run build
   ```
   Should complete without errors.

3. **Commit Changes:**
   ```bash
   git add content/posts/[slug].mdx
   git commit -m "Publish: [Post Title]"
   git push origin main
   ```

#### Automatic Deployment

If deployed on Vercel (recommended):
- Push to main branch triggers automatic deployment
- Build time: ~2-3 minutes
- Deployment URL: Production domain

### 8. Verify Live Publication

After deployment completes:

1. **Check Blog Index:**
   - Visit: `https://infinitycards.com/blog`
   - Verify post appears in list
   - Check thumbnail and metadata

2. **Check Individual Post:**
   - Visit: `https://infinitycards.com/blog/[slug]`
   - Verify all content renders correctly
   - Test all interactive elements

3. **SEO Verification:**
   ```bash
   # Check meta tags
   curl -s https://infinitycards.com/blog/[slug] | grep "meta"

   # Verify in Google Search Console (after 24-48 hours)
   ```

4. **Social Sharing Test:**
   - Share on Twitter/X
   - Share on LinkedIn
   - Share on Facebook
   - Verify OG image and description display

5. **Analytics Verification:**
   - Google Analytics: Check pageview events
   - Verify tracking code fires
   - Confirm event parameters (title, category)

### 9. Post-Publication Tasks

#### Submit to Search Engines

1. **Google Search Console:**
   - Submit URL for indexing
   - Request indexing for new/updated pages

2. **Sitemap:**
   - Automatically updated at: `/sitemap.xml`
   - Google crawls periodically

#### Promote Content

- [ ] Share on social media (TikTok, Twitter, LinkedIn)
- [ ] Email newsletter (if applicable)
- [ ] Internal links from related posts
- [ ] Community forums/Discord
- [ ] Consider paid promotion for high-value content

#### Monitor Performance

Track metrics in Google Analytics:
- Pageviews
- Average time on page
- Bounce rate
- Traffic sources
- Conversions (if applicable)

## Content Management System Access

### File System Access

**Location:** Local file system (Git-based)

**Directory Structure:**
```
blog/
├── content/
│   └── posts/          # All blog posts (.mdx files)
└── public/
    └── images/
        └── blog/       # Blog images and featured images
```

**Access Requirements:**
- Git repository access
- Text editor (VS Code recommended)
- Node.js for local preview
- Vercel deployment access (for production)

### Permissions

**Content Creators:**
- Create/edit MDX files in `content/posts/`
- Upload images to `public/images/blog/`
- Preview on local dev server

**Developers:**
- Full repository access
- Deployment configuration
- Build pipeline management

## Troubleshooting

### Common Issues

**Post Not Appearing:**
- Check `published: true` in frontmatter
- Verify file is in `content/posts/` directory
- Ensure file has `.mdx` extension
- Check for frontmatter syntax errors

**Build Errors:**
- Validate YAML frontmatter syntax
- Check for unclosed code blocks
- Verify all images exist in `/public`
- Review error logs: `npm run build`

**Image Not Loading:**
- Verify image path starts with `/`
- Check file exists in `public/` directory
- Ensure proper file extension
- Optimize file size (< 200KB)

**Broken Links:**
- Use relative URLs for internal links
- Verify external URLs are accessible
- Test all links before publishing

## Best Practices

### Content Strategy

1. **Consistency:** Publish regularly (weekly recommended)
2. **Quality over Quantity:** Focus on valuable, in-depth content
3. **Audience-First:** Write for your readers, not search engines
4. **Data-Driven:** Use analytics to guide content decisions
5. **Evergreen Content:** Create content with long-term value

### SEO Optimization

1. **Keyword Research:** Use tools like Ahrefs, SEMrush, Google Keyword Planner
2. **Long-Tail Keywords:** Target specific, lower-competition phrases
3. **Internal Linking:** Link to 2-3 related posts in each article
4. **External Links:** Cite authoritative sources
5. **Update Old Content:** Refresh posts annually to maintain relevance

### Writing Tips

1. **Hook Readers:** Start with a compelling opening
2. **Scannable Format:** Use headings, bullets, and short paragraphs
3. **Actionable Insights:** Provide practical takeaways
4. **Conversational Tone:** Write like you speak (professional but approachable)
5. **Proofread Thoroughly:** Use Grammarly or similar tools

## Quick Reference

### File Paths

| Item | Path |
|------|------|
| Blog Posts | `blog/content/posts/*.mdx` |
| Blog Images | `blog/public/images/blog/*.jpg` |
| Local Dev Server | `http://localhost:3001` |
| Production Blog | `https://infinitycards.com/blog` |

### Essential Commands

```bash
# Start dev server
cd blog && npm run dev

# Build for production
npm run build

# Check for errors
npm run lint

# Format code
npm run format
```

### Support

For technical issues or questions:
- Check README.md for general documentation
- Review existing posts for examples
- Contact development team for build/deployment issues

---

**Last Updated:** February 26, 2024
**Version:** 1.0
**Maintained By:** Infinity Cards Development Team
