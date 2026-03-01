# Blog Platform Deployment Guide

This guide covers deploying the Infinity Cards blog platform to Vercel (recommended) or alternative hosting platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Vercel Deployment](#vercel-deployment)
- [Environment Variables](#environment-variables)
- [Custom Domain Setup](#custom-domain-setup)
- [Alternative Hosting](#alternative-hosting)
- [Post-Deployment Verification](#post-deployment-verification)
- [Troubleshooting](#troubleshooting)
- [Continuous Deployment](#continuous-deployment)

## Prerequisites

Before deploying, ensure you have:

- [ ] Node.js 20+ installed locally
- [ ] Git repository initialized and pushed to GitHub/GitLab/Bitbucket
- [ ] Vercel account (free tier works fine for most use cases)
- [ ] All environment variables configured (see [Environment Variables](#environment-variables))
- [ ] Production build tested locally (`npm run build && npm start`)
- [ ] Google Analytics 4 property created (optional but recommended)

## Vercel Deployment

Vercel is the recommended hosting platform for this Next.js blog as it provides:
- Zero-configuration deployments
- Automatic HTTPS
- Global CDN
- Instant rollbacks
- Preview deployments for PRs

### Method 1: Deploy via Vercel Dashboard (Recommended)

1. **Connect Your Repository**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your Git repository
   - Select the `blog` directory as the root directory

2. **Configure Build Settings**
   - Framework Preset: Next.js (auto-detected)
   - Build Command: `npm run build` (auto-configured)
   - Output Directory: `.next` (auto-configured)
   - Install Command: `npm install` (auto-configured)
   - Root Directory: `blog` (if monorepo)

3. **Add Environment Variables**
   - Click "Environment Variables"
   - Add the following (see [Environment Variables](#environment-variables) section):
     - `NEXT_PUBLIC_SITE_URL`
     - `NEXT_PUBLIC_BLOG_NAME`
     - `NEXT_PUBLIC_BLOG_DESCRIPTION`
     - `NEXT_PUBLIC_GA_MEASUREMENT_ID` (optional)

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for the build to complete
   - Your blog will be live at `https://your-project.vercel.app`

### Method 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from Blog Directory**
   ```bash
   cd blog
   vercel
   ```

4. **Follow the prompts:**
   - Set up and deploy: Yes
   - Which scope: Select your account
   - Link to existing project: No (first time) or Yes (subsequent deploys)
   - Project name: infinity-cards-blog (or your preferred name)
   - In which directory is your code located: ./
   - Want to override the settings: No

5. **Deploy to Production**
   ```bash
   vercel --prod
   ```

## Environment Variables

Configure the following environment variables in your Vercel project settings:

### Required Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `NEXT_PUBLIC_SITE_URL` | Production site URL | `https://infinitycards.com` or `https://blog.infinitycards.com` |
| `NEXT_PUBLIC_BLOG_NAME` | Blog name for SEO | `Infinity Cards Blog` |
| `NEXT_PUBLIC_BLOG_DESCRIPTION` | Blog description for SEO | `Expert insights on trading card games, tournament preparation, and collection management` |

### Optional Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `NEXT_PUBLIC_GA_MEASUREMENT_ID` | Google Analytics 4 Measurement ID | `G-XXXXXXXXXX` |

### Setting Environment Variables in Vercel

**Via Dashboard:**
1. Go to your project in Vercel
2. Navigate to Settings → Environment Variables
3. Add each variable with its value
4. Select which environments (Production, Preview, Development)
5. Click "Save"

**Via CLI:**
```bash
vercel env add NEXT_PUBLIC_SITE_URL production
# Enter value when prompted: https://infinitycards.com

vercel env add NEXT_PUBLIC_GA_MEASUREMENT_ID production
# Enter value when prompted: G-XXXXXXXXXX
```

## Custom Domain Setup

### Option 1: Subdomain (blog.infinitycards.com)

1. **Add Domain in Vercel**
   - Go to Project Settings → Domains
   - Add domain: `blog.infinitycards.com`
   - Vercel will provide DNS records

2. **Configure DNS**
   - Go to your domain registrar (e.g., Namecheap, GoDaddy)
   - Add CNAME record:
     - Type: `CNAME`
     - Name: `blog`
     - Value: `cname.vercel-dns.com`
     - TTL: `3600` (1 hour)

3. **Wait for Propagation**
   - DNS changes can take 1-48 hours
   - Check status in Vercel dashboard

### Option 2: Subdirectory (infinitycards.com/blog)

If your main site is hosted elsewhere and you want the blog at `/blog`:

1. **Configure Main Site Reverse Proxy**

   **For Nginx:**
   ```nginx
   location /blog {
       proxy_pass https://your-blog.vercel.app;
       proxy_set_header Host your-blog.vercel.app;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
   }
   ```

   **For Apache:**
   ```apache
   ProxyPass /blog https://your-blog.vercel.app
   ProxyPassReverse /blog https://your-blog.vercel.app
   ```

2. **Update Environment Variables**
   ```
   NEXT_PUBLIC_SITE_URL=https://infinitycards.com
   ```

3. **Configure Next.js Base Path** (if needed)
   Update `next.config.js`:
   ```javascript
   const nextConfig = {
     basePath: '/blog',
     // ... other config
   }
   ```

### Option 3: Apex Domain (infinitycards.com)

1. **Add Domain in Vercel**
   - Add `infinitycards.com` in Domains settings

2. **Configure DNS**
   - Add A records (provided by Vercel):
     - Type: `A`
     - Name: `@`
     - Value: `76.76.21.21` (example - use Vercel's actual IPs)

## Alternative Hosting

### Self-Hosted (Node.js)

1. **Build the Application**
   ```bash
   npm run build
   ```

2. **Start the Server**
   ```bash
   npm start
   ```

3. **Use Process Manager (PM2)**
   ```bash
   npm install -g pm2
   pm2 start npm --name "infinity-blog" -- start
   pm2 save
   pm2 startup
   ```

4. **Configure Reverse Proxy** (Nginx/Apache)
   ```nginx
   server {
       listen 80;
       server_name blog.infinitycards.com;

       location / {
           proxy_pass http://localhost:3001;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

### Docker Deployment

1. **Create Dockerfile** (in blog directory)
   ```dockerfile
   FROM node:20-alpine AS base

   # Dependencies
   FROM base AS deps
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci

   # Builder
   FROM base AS builder
   WORKDIR /app
   COPY --from=deps /app/node_modules ./node_modules
   COPY . .
   RUN npm run build

   # Runner
   FROM base AS runner
   WORKDIR /app
   ENV NODE_ENV=production

   RUN addgroup --system --gid 1001 nodejs
   RUN adduser --system --uid 1001 nextjs

   COPY --from=builder /app/public ./public
   COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
   COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

   USER nextjs
   EXPOSE 3001
   ENV PORT=3001

   CMD ["node", "server.js"]
   ```

2. **Build and Run**
   ```bash
   docker build -t infinity-blog .
   docker run -p 3001:3001 \
     -e NEXT_PUBLIC_SITE_URL=https://infinitycards.com \
     -e NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX \
     infinity-blog
   ```

### Static Export (CDN Hosting)

Note: Some features require a Node.js server. Static export has limitations.

1. **Configure Static Export**
   Update `next.config.js`:
   ```javascript
   const nextConfig = {
     output: 'export',
     images: {
       unoptimized: true,
     },
   }
   ```

2. **Build Static Files**
   ```bash
   npm run build
   ```

3. **Deploy to CDN**
   - Upload `out` directory to S3, Netlify, Cloudflare Pages, etc.

## Post-Deployment Verification

After deployment, verify the following:

### 1. Basic Functionality
- [ ] Home page loads correctly
- [ ] Blog listing page displays all posts
- [ ] Individual blog posts load and render properly
- [ ] Navigation menu works
- [ ] Footer links are functional

### 2. Performance
- [ ] Test with [PageSpeed Insights](https://pagespeed.web.dev/)
  - Mobile score > 80
  - Desktop score > 90
- [ ] Check Core Web Vitals
  - LCP < 2.5s
  - FID < 100ms
  - CLS < 0.1

### 3. SEO
- [ ] Verify meta tags (view page source)
- [ ] Check sitemap: `https://your-domain.com/sitemap.xml`
- [ ] Check robots.txt: `https://your-domain.com/robots.txt`
- [ ] Test structured data with [Rich Results Test](https://search.google.com/test/rich-results)
- [ ] Verify Open Graph tags with [OpenGraph.xyz](https://www.opengraph.xyz/)

### 4. Analytics
- [ ] Google Analytics tracking is firing
- [ ] Test with GA4 DebugView
- [ ] Verify events are being captured

### 5. Mobile Responsiveness
- [ ] Test on mobile devices
- [ ] Check with Chrome DevTools device emulator
- [ ] Verify touch targets are appropriately sized

### 6. Security
- [ ] HTTPS enabled and certificate valid
- [ ] Security headers present (check with [securityheaders.com](https://securityheaders.com))
- [ ] No mixed content warnings

## Troubleshooting

### Build Failures

**Problem:** Build fails with "Module not found"
```
Solution:
1. Clear node_modules and reinstall
   npm ci
2. Check for missing dependencies in package.json
3. Verify all imports use correct paths
```

**Problem:** Build fails with TypeScript errors
```
Solution:
1. Run type checking locally
   npm run build
2. Fix all type errors before deploying
3. Ensure tsconfig.json is properly configured
```

### Runtime Errors

**Problem:** 404 errors on blog posts
```
Solution:
1. Verify content files exist in content/posts/
2. Check file naming convention (kebab-case.mdx)
3. Ensure frontmatter is properly formatted
4. Clear Vercel build cache and redeploy
```

**Problem:** Images not loading
```
Solution:
1. Verify images are in public/ directory
2. Check next.config.js image configuration
3. Ensure image paths start with /
4. For external images, add domain to remotePatterns
```

### Performance Issues

**Problem:** Slow page loads
```
Solution:
1. Enable image optimization
2. Implement code splitting
3. Use dynamic imports for heavy components
4. Enable Vercel Analytics to identify bottlenecks
5. Optimize images (use WebP/AVIF formats)
```

### Environment Variable Issues

**Problem:** Environment variables not working
```
Solution:
1. Ensure variables start with NEXT_PUBLIC_ for client-side access
2. Redeploy after adding new variables
3. Check variable names match exactly (case-sensitive)
4. Verify variables are set for correct environment (Production/Preview)
```

## Continuous Deployment

### Automatic Deployments

Vercel automatically deploys when you push to your repository:

- **Push to main/master** → Production deployment
- **Push to any branch** → Preview deployment
- **Pull request** → Preview deployment with unique URL

### Deployment Protection

Configure deployment protection in Vercel:

1. **Branch Protection**
   - Protect `main` branch in GitHub
   - Require PR reviews before merging
   - Require status checks to pass

2. **Vercel Protection**
   - Enable password protection for preview deployments
   - Set up deployment notifications
   - Configure automatic rollback on errors

### Rollback Strategy

If a deployment has issues:

1. **Via Vercel Dashboard**
   - Go to Deployments
   - Find last working deployment
   - Click "..." → "Promote to Production"

2. **Via Git**
   ```bash
   git revert HEAD
   git push origin main
   ```

## Monitoring & Maintenance

### Regular Checks

- **Weekly:** Review analytics for traffic and errors
- **Monthly:** Update dependencies (`npm update`)
- **Quarterly:** Performance audit with Lighthouse
- **As needed:** Content updates via MDX files

### Alerts & Monitoring

Set up monitoring for:
- Uptime monitoring (UptimeRobot, Pingdom)
- Error tracking (Sentry, LogRocket)
- Performance monitoring (Vercel Analytics)
- SEO monitoring (Google Search Console)

## Support & Resources

- **Next.js Documentation:** https://nextjs.org/docs
- **Vercel Documentation:** https://vercel.com/docs
- **Vercel Support:** https://vercel.com/support
- **Project README:** See README.md in this directory

---

**Last Updated:** February 2025
**Maintained by:** Infinity Cards Development Team
