# Blog Platform QA Checklist

This comprehensive QA checklist covers testing the blog platform across multiple devices, browsers, and functionality areas to ensure production readiness.

**Test Date:** _________________
**Tester Name:** _________________
**Environment:** □ Local Dev  □ Staging  □ Production
**Test URL:** _________________

---

## Table of Contents

1. [Mobile Testing](#mobile-testing)
2. [Desktop Testing](#desktop-testing)
3. [Performance Testing](#performance-testing)
4. [CMS & Content Management](#cms--content-management)
5. [Analytics Tracking](#analytics-tracking)
6. [SEO Verification](#seo-verification)
7. [Accessibility](#accessibility)
8. [Security](#security)
9. [Cross-Browser Compatibility](#cross-browser-compatibility)
10. [User Experience](#user-experience)

---

## Mobile Testing

### iOS Safari (iPhone/iPad)

**Test Devices:**
- [ ] iPhone (iOS 15+)
- [ ] iPad (iOS 15+)

**Blog Index Page** (`/blog`)
- [ ] Page loads successfully
- [ ] Layout is responsive and displays correctly
- [ ] All images load properly
- [ ] Category filter buttons work
- [ ] Blog cards are tappable
- [ ] Navigation menu works
- [ ] Footer displays correctly
- [ ] No horizontal scrolling issues
- [ ] Text is readable (font size adequate)
- [ ] Touch targets are adequate size (min 44x44px)

**Individual Blog Post** (`/blog/[slug]`)
- [ ] Post loads successfully
- [ ] Featured image displays correctly
- [ ] Typography is readable and properly sized
- [ ] Table of contents works on tap
- [ ] Share buttons work (Twitter, Facebook, LinkedIn)
- [ ] Related posts section displays
- [ ] Breadcrumbs are functional
- [ ] Inline images load and scale properly
- [ ] Code blocks are scrollable/readable
- [ ] Lists and blockquotes display correctly
- [ ] Internal links work
- [ ] External links open in new tab

**Category Pages** (`/blog/category/[category]`)
- [ ] Category pages load successfully
- [ ] Breadcrumbs work
- [ ] Filtered posts display correctly
- [ ] Category badge displays
- [ ] "Back to all posts" link works

**Performance on Mobile**
- [ ] Page load time < 3 seconds on 4G
- [ ] Images lazy load properly
- [ ] Smooth scrolling
- [ ] No janky animations
- [ ] No layout shifts (CLS)

**iOS-Specific Issues**
- [ ] No fixed positioning bugs
- [ ] Viewport height works correctly
- [ ] Touch events work (no double-tap zoom on buttons)
- [ ] Safari reader mode available for posts
- [ ] Add to home screen works (if PWA)

---

### Android Chrome

**Test Devices:**
- [ ] Android phone (Android 10+)
- [ ] Android tablet (Android 10+)

**Blog Index Page** (`/blog`)
- [ ] Page loads successfully
- [ ] Layout is responsive and displays correctly
- [ ] All images load properly
- [ ] Category filter buttons work
- [ ] Blog cards are tappable
- [ ] Navigation menu works
- [ ] Footer displays correctly
- [ ] No horizontal scrolling issues
- [ ] Text is readable (font size adequate)
- [ ] Material design elements work properly

**Individual Blog Post** (`/blog/[slug]`)
- [ ] Post loads successfully
- [ ] Featured image displays correctly
- [ ] Typography is readable and properly sized
- [ ] Table of contents works on tap
- [ ] Share buttons work (Twitter, Facebook, LinkedIn)
- [ ] Related posts section displays
- [ ] Breadcrumbs are functional
- [ ] Inline images load and scale properly
- [ ] Code blocks are scrollable/readable
- [ ] Android share menu integration works

**Category Pages** (`/blog/category/[category]`)
- [ ] Category pages load successfully
- [ ] Breadcrumbs work
- [ ] Filtered posts display correctly
- [ ] Category badge displays

**Performance on Mobile**
- [ ] Page load time < 3 seconds on 4G
- [ ] Images lazy load properly
- [ ] Smooth scrolling
- [ ] No janky animations
- [ ] No layout shifts (CLS)

**Android-Specific Issues**
- [ ] Back button navigation works correctly
- [ ] Chrome autofill works (if forms present)
- [ ] Native share sheet integration works
- [ ] App banner works (if applicable)

---

## Desktop Testing

### Chrome (Latest Version)

**Homepage** (`/`)
- [ ] Homepage loads successfully
- [ ] Header displays correctly
- [ ] Footer displays correctly
- [ ] Navigation links work
- [ ] Layout is properly centered/responsive

**Blog Index Page** (`/blog`)
- [ ] Page loads successfully
- [ ] Grid layout displays correctly (3 columns on desktop)
- [ ] All images load properly
- [ ] Category filter works
- [ ] Hover effects work on blog cards
- [ ] Pagination works (if implemented)
- [ ] Post metadata displays (date, author, read time)

**Individual Blog Post** (`/blog/[slug]`)
- [ ] Post loads successfully
- [ ] Sidebar displays on desktop (table of contents)
- [ ] Featured image displays at proper size
- [ ] Typography is readable with proper line height
- [ ] Table of contents sticky behavior works
- [ ] Active heading highlights in TOC
- [ ] Share buttons work
- [ ] Copy link functionality works
- [ ] Related posts display
- [ ] Code syntax highlighting works
- [ ] Tables render properly
- [ ] Blockquotes styled correctly

**Category Pages** (`/blog/category/[category]`)
- [ ] Category pages load successfully
- [ ] Grid layout works
- [ ] Breadcrumbs display and work
- [ ] Category description displays

**Developer Console**
- [ ] No JavaScript errors in console
- [ ] No 404 errors for assets
- [ ] No mixed content warnings
- [ ] No CORS errors

---

### Firefox (Latest Version)

**Blog Index Page** (`/blog`)
- [ ] Page loads successfully
- [ ] Layout displays correctly
- [ ] Images load properly
- [ ] CSS grid/flexbox works
- [ ] Filters work
- [ ] Hover states work

**Individual Blog Post** (`/blog/[slug]`)
- [ ] Post loads successfully
- [ ] Sidebar layout works
- [ ] Typography renders correctly
- [ ] Share buttons work
- [ ] Table of contents works
- [ ] Code blocks display with syntax highlighting
- [ ] Custom fonts load

**Category Pages** (`/blog/category/[category]`)
- [ ] Category pages load and display correctly
- [ ] All functionality works

**Firefox-Specific Checks**
- [ ] Reader mode available and works
- [ ] CSS custom properties work
- [ ] Font rendering acceptable
- [ ] No Firefox-specific layout bugs

---

### Safari (macOS)

**Blog Index Page** (`/blog`)
- [ ] Page loads successfully
- [ ] Layout displays correctly
- [ ] Images load properly
- [ ] WebP images work (or fallback)
- [ ] Filters work
- [ ] Hover states work

**Individual Blog Post** (`/blog/[slug]`)
- [ ] Post loads successfully
- [ ] Sidebar layout works
- [ ] Typography renders correctly
- [ ] Share buttons work
- [ ] Table of contents works
- [ ] Code blocks display correctly

**Category Pages** (`/blog/category/[category]`)
- [ ] Category pages load and display correctly
- [ ] All functionality works

**Safari-Specific Checks**
- [ ] Webkit-specific CSS works
- [ ] No font rendering issues
- [ ] Smooth scrolling works
- [ ] Reader mode available
- [ ] Privacy features don't block functionality

---

## Performance Testing

### Page Load Speed

Use [Google PageSpeed Insights](https://pagespeed.web.dev/) or [Lighthouse](https://developer.chrome.com/docs/lighthouse/)

**Mobile Performance**
- [ ] Performance score > 80
- [ ] First Contentful Paint (FCP) < 1.8s
- [ ] Largest Contentful Paint (LCP) < 2.5s
- [ ] Total Blocking Time (TBT) < 300ms
- [ ] Cumulative Layout Shift (CLS) < 0.1
- [ ] Speed Index < 3.4s
- [ ] Time to Interactive (TTI) < 3.8s
- [ ] **Total page load time < 3 seconds**

**Desktop Performance**
- [ ] Performance score > 90
- [ ] First Contentful Paint (FCP) < 1.2s
- [ ] Largest Contentful Paint (LCP) < 1.2s
- [ ] Total Blocking Time (TBT) < 150ms
- [ ] Cumulative Layout Shift (CLS) < 0.1
- [ ] Speed Index < 1.3s

**Test URLs:**
- [ ] Homepage: `/`
- [ ] Blog index: `/blog`
- [ ] Sample blog post: `/blog/[slug]`
- [ ] Category page: `/blog/category/[category]`

**Performance Optimizations Verified**
- [ ] Images use Next.js Image component
- [ ] Images are lazy loaded (except above-fold)
- [ ] Modern image formats (AVIF/WebP) used
- [ ] Fonts are preloaded
- [ ] CSS is minified
- [ ] JavaScript is minified and code-split
- [ ] No render-blocking resources
- [ ] Critical CSS inlined (if applicable)

**Network Performance**
- [ ] Test on fast 4G (throttling in DevTools)
- [ ] Test on slow 3G (throttling in DevTools)
- [ ] All assets load over HTTPS
- [ ] Gzip/Brotli compression enabled
- [ ] Cache headers set correctly

---

## CMS & Content Management

### Content Publishing Workflow

**Prerequisites**
- [ ] CONTENT_WORKFLOW.md documentation reviewed
- [ ] Access to content directory (`content/posts/`)
- [ ] MDX file format understood

**Creating New Blog Post**
- [ ] Create new MDX file in `content/posts/`
- [ ] Add required frontmatter fields:
  - [ ] title
  - [ ] description
  - [ ] date
  - [ ] category
  - [ ] tags (array)
  - [ ] author
  - [ ] image
  - [ ] published (boolean)
- [ ] Write post content in Markdown/MDX
- [ ] Add images to `public/images/blog/`
- [ ] Reference images correctly in content

**Preview & Testing**
- [ ] Run dev server: `npm run dev`
- [ ] Navigate to new post URL: `/blog/[slug]`
- [ ] Verify post displays correctly
- [ ] Check all metadata displays
- [ ] Verify images load
- [ ] Test all links (internal and external)
- [ ] Verify category badge displays
- [ ] Check tags display
- [ ] Test share buttons
- [ ] Verify related posts appear

**Publishing**
- [ ] Set `published: true` in frontmatter
- [ ] Run production build: `npm run build`
- [ ] Verify build succeeds with no errors
- [ ] Commit changes to Git
- [ ] Push to deployment branch
- [ ] Verify automatic deployment triggered
- [ ] Check deployment logs for errors

**Post-Publication Verification**
- [ ] Post appears on blog index (`/blog`)
- [ ] Post accessible at correct URL
- [ ] Post appears in correct category page
- [ ] Post appears in sitemap (`/sitemap.xml`)
- [ ] Meta tags correct in page source
- [ ] Open Graph tags correct
- [ ] Structured data validates

**Unpublishing/Draft Mode**
- [ ] Set `published: false` in frontmatter
- [ ] Verify post no longer appears on blog index
- [ ] Verify post returns 404 when accessed directly
- [ ] Verify post removed from sitemap

**Editing Existing Post**
- [ ] Modify content in MDX file
- [ ] Update `date` field (or add `lastModified`)
- [ ] Save changes
- [ ] Verify changes appear in dev mode
- [ ] Build and deploy
- [ ] Verify changes live in production

**Category Management**
- [ ] Create post with new category
- [ ] Verify category appears in filter on `/blog`
- [ ] Verify category page created at `/blog/category/[new-category]`
- [ ] Add category description in category page code (if needed)

**Tag Management**
- [ ] Add tags to post frontmatter
- [ ] Verify tags display on post page
- [ ] Verify tags searchable/filterable (if implemented)

---

## Analytics Tracking

### Google Analytics 4 Setup

**Configuration**
- [ ] `NEXT_PUBLIC_GA_MEASUREMENT_ID` set in environment variables
- [ ] GA4 property created in Google Analytics
- [ ] Data stream configured for website

**Pageview Tracking**

Open Google Analytics in Real-Time view: [analytics.google.com](https://analytics.google.com/)

- [ ] Navigate to homepage → verify pageview event
- [ ] Navigate to `/blog` → verify pageview event
- [ ] Navigate to `/blog/[slug]` → verify pageview event
- [ ] Navigate to `/blog/category/[category]` → verify pageview event
- [ ] Verify `page_title` parameter populated
- [ ] Verify `page_location` parameter correct
- [ ] Verify `page_path` parameter correct

**Event Tracking**

Test custom events (if implemented in components):

- [ ] Blog post view event fires (event: `blog_post_view`)
  - [ ] `slug` parameter populated
  - [ ] `title` parameter populated
  - [ ] `category` parameter populated
- [ ] Social share events fire (event: `share`)
  - [ ] Twitter share tracked
  - [ ] Facebook share tracked
  - [ ] LinkedIn share tracked
  - [ ] Copy link tracked
  - [ ] `method` parameter correct
- [ ] Category filter event fires (event: `category_filter`)
  - [ ] `category` parameter populated
- [ ] Outbound link clicks tracked (event: `click`)
  - [ ] `link_url` parameter populated
  - [ ] `outbound: true` parameter set
- [ ] Time on page tracked (if implemented)

**User Demographics**
- [ ] Real-time users showing in dashboard
- [ ] Location data populating
- [ ] Device category tracking (mobile/desktop/tablet)
- [ ] Browser tracking
- [ ] OS tracking

**Debugging**
- [ ] Enable GA debug mode (add `?debug_mode=1` to URL)
- [ ] Open browser console
- [ ] Verify gtag events logged
- [ ] No GA-related JavaScript errors

**Privacy Compliance**
- [ ] Cookie consent banner implemented (if required)
- [ ] Privacy policy mentions GA tracking
- [ ] Data retention settings configured in GA4
- [ ] IP anonymization enabled (if required)

---

## SEO Verification

### Meta Tags

Test each page type and verify meta tags in page source (View Source or inspect `<head>`):

**Homepage** (`/`)
- [ ] `<title>` tag present and descriptive
- [ ] `<meta name="description">` present (150-160 chars)
- [ ] `<meta name="viewport">` set correctly
- [ ] Favicon present
- [ ] Canonical URL set

**Blog Index** (`/blog`)
- [ ] `<title>` tag present and descriptive
- [ ] `<meta name="description">` present
- [ ] Canonical URL set (`/blog`)

**Individual Blog Post** (`/blog/[slug]`)
- [ ] `<title>` tag present (post title + site name)
- [ ] `<meta name="description">` present (post description)
- [ ] `<meta name="author">` present
- [ ] `<meta name="keywords">` present (tags)
- [ ] Canonical URL set correctly
- [ ] `<meta name="robots">` allows indexing

**Category Page** (`/blog/category/[category]`)
- [ ] `<title>` tag present (category name + site name)
- [ ] `<meta name="description">` present
- [ ] Canonical URL set correctly

### Open Graph Tags

Test with [Open Graph Debugger](https://www.opengraph.xyz/) or Facebook Sharing Debugger

**Blog Post Page**
- [ ] `og:title` present and correct
- [ ] `og:description` present and correct
- [ ] `og:image` present (1200x630px recommended)
- [ ] `og:url` present and correct
- [ ] `og:type` set to `article`
- [ ] `og:site_name` present
- [ ] `article:published_time` present
- [ ] `article:author` present
- [ ] `article:section` (category) present
- [ ] `article:tag` present for each tag

**Other Pages**
- [ ] `og:title` present
- [ ] `og:description` present
- [ ] `og:image` present
- [ ] `og:url` correct
- [ ] `og:type` set appropriately

### Twitter Card Tags

- [ ] `twitter:card` set (summary_large_image recommended)
- [ ] `twitter:title` present
- [ ] `twitter:description` present
- [ ] `twitter:image` present
- [ ] `twitter:site` present (if Twitter account exists)
- [ ] `twitter:creator` present (if author has Twitter)

Test with [Twitter Card Validator](https://cards-dev.twitter.com/validator)

### Sitemap

**Sitemap Access**
- [ ] `/sitemap.xml` accessible
- [ ] Valid XML format (no syntax errors)
- [ ] All published blog posts included
- [ ] All category pages included
- [ ] Homepage and blog index included
- [ ] URLs are absolute (include full domain)
- [ ] `<lastmod>` dates present and correct
- [ ] `<priority>` values set appropriately
- [ ] `<changefreq>` values set appropriately

**Sitemap Submission**
- [ ] Submit to Google Search Console
- [ ] Submit to Bing Webmaster Tools
- [ ] Verify sitemap processed without errors

### Robots.txt

**Robots.txt Access**
- [ ] `/robots.txt` accessible
- [ ] Allows all search engines (`User-agent: *`)
- [ ] Allows crawling of blog content
- [ ] Blocks `/api/` routes
- [ ] Blocks `/_next/` routes
- [ ] Blocks AI crawlers (GPTBot) if desired
- [ ] Sitemap URL listed in robots.txt

**Robots Meta Tags**
- [ ] Published posts have `index, follow`
- [ ] Draft posts have `noindex, nofollow`
- [ ] Admin/private pages blocked from indexing

### Structured Data (Schema.org)

Test with [Google Rich Results Test](https://search.google.com/test/rich-results) or [Schema Markup Validator](https://validator.schema.org/)

**Blog Post Page**
- [ ] Article schema present (type: `BlogPosting` or `Article`)
- [ ] `headline` property present
- [ ] `author` property present (Person schema)
- [ ] `datePublished` property present (ISO 8601 format)
- [ ] `dateModified` property present (if applicable)
- [ ] `image` property present (ImageObject)
- [ ] `publisher` property present (Organization with logo)
- [ ] `description` property present
- [ ] `mainEntityOfPage` property present
- [ ] `wordCount` property present
- [ ] `keywords` property present
- [ ] No errors in Google Rich Results Test
- [ ] Eligible for Article rich results

**Breadcrumb Schema**
- [ ] BreadcrumbList schema present
- [ ] All breadcrumb items included
- [ ] Position indexes correct (start at 1)
- [ ] Item URLs correct

**Additional Schema Types** (if applicable)
- [ ] Organization schema on homepage
- [ ] WebSite schema on homepage
- [ ] CollectionPage schema on category pages

### Search Console Setup

- [ ] Site verified in Google Search Console
- [ ] Sitemap submitted and indexed
- [ ] No coverage errors
- [ ] No mobile usability errors
- [ ] Core Web Vitals passing
- [ ] No manual actions/penalties

### On-Page SEO

**Blog Post Content**
- [ ] H1 heading present (post title)
- [ ] Logical heading hierarchy (H1 → H2 → H3)
- [ ] Internal links to related posts
- [ ] External links open in new tab (`target="_blank"`)
- [ ] External links have `rel="noopener noreferrer"`
- [ ] Images have descriptive alt text
- [ ] URLs are clean and descriptive (slug-based)
- [ ] Content is unique and high-quality
- [ ] Keyword usage natural and relevant

---

## Accessibility

### WCAG 2.1 Level AA Compliance

**Keyboard Navigation**
- [ ] All interactive elements focusable with Tab
- [ ] Focus indicators visible on all elements
- [ ] Tab order logical
- [ ] Escape key closes modals (if applicable)
- [ ] No keyboard traps
- [ ] Skip to content link present (recommended)

**Screen Reader Testing**

Test with screen readers (NVDA on Windows, VoiceOver on Mac/iOS, TalkBack on Android):

- [ ] All images have descriptive alt text
- [ ] Decorative images have empty alt (`alt=""`)
- [ ] Links have descriptive text (no "click here")
- [ ] Form labels associated correctly (if forms present)
- [ ] Headings announce hierarchy correctly
- [ ] ARIA landmarks used appropriately
- [ ] ARIA labels present where needed
- [ ] No ARIA misuse

**Color Contrast**

Test with [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/):

- [ ] Body text contrast ratio ≥ 4.5:1
- [ ] Large text (18pt+) contrast ratio ≥ 3:1
- [ ] Interactive elements contrast ratio ≥ 4.5:1
- [ ] Focus indicators contrast ratio ≥ 3:1
- [ ] Color not sole indicator of information

**Visual**
- [ ] Text resizable to 200% without breaking layout
- [ ] No horizontal scrolling at 320px width
- [ ] No text in images (or has alternative)
- [ ] Line height adequate (1.5+ for body text)
- [ ] Paragraph spacing adequate

**Forms & Interactive Elements** (if applicable)
- [ ] Error messages descriptive and helpful
- [ ] Required fields indicated clearly
- [ ] Form validation accessible
- [ ] Success messages announced to screen readers

**Automated Testing**

Run [axe DevTools](https://www.deque.com/axe/devtools/) or [WAVE](https://wave.webaim.org/):

- [ ] No critical violations
- [ ] No serious violations
- [ ] Moderate/minor issues documented and reviewed
- [ ] Best practice recommendations reviewed

---

## Security

### HTTPS & SSL

**SSL Certificate**
- [ ] Site loads over HTTPS (https://)
- [ ] Valid SSL certificate (not expired)
- [ ] Certificate matches domain
- [ ] No mixed content warnings
- [ ] All assets load over HTTPS
- [ ] HTTP redirects to HTTPS automatically

Test with [SSL Labs](https://www.ssllabs.com/ssltest/):
- [ ] SSL rating A or A+
- [ ] TLS 1.2 or higher supported
- [ ] No weak cipher suites

### Security Headers

Test with [Security Headers](https://securityheaders.com/):

- [ ] `X-Content-Type-Options: nosniff` header present
- [ ] `X-Frame-Options: DENY` or `SAMEORIGIN` header present
- [ ] `X-XSS-Protection: 1; mode=block` header present
- [ ] `Referrer-Policy` header present
- [ ] `Permissions-Policy` header present
- [ ] `Content-Security-Policy` header present (recommended)
- [ ] `Strict-Transport-Security` header present (HSTS)

**Content Security**
- [ ] No sensitive data exposed in client-side code
- [ ] API keys not visible in source code
- [ ] Environment variables properly secured
- [ ] No debug/test code in production

**External Resources**
- [ ] All third-party scripts loaded over HTTPS
- [ ] External scripts use SRI hashes (if critical)
- [ ] External images from trusted sources
- [ ] CDN resources secure and verified

---

## Cross-Browser Compatibility

### Browser Testing Matrix

Test on the following browsers at minimum:

| Browser | Version | Desktop | Mobile | Status |
|---------|---------|---------|--------|--------|
| Chrome | Latest | ☐ | ☐ | |
| Firefox | Latest | ☐ | ☐ | |
| Safari | Latest | ☐ | ☐ | |
| Edge | Latest | ☐ | N/A | |
| Samsung Internet | Latest | N/A | ☐ | |
| Chrome Android | Latest | N/A | ☐ | |
| Safari iOS | Latest | N/A | ☐ | |

**Cross-Browser Issues to Check**
- [ ] CSS Grid support and layout consistency
- [ ] Flexbox behavior consistent
- [ ] Custom fonts load in all browsers
- [ ] JavaScript features work (ES6+ support)
- [ ] Smooth scrolling works or degrades gracefully
- [ ] CSS custom properties (variables) work
- [ ] Backdrop filters work or have fallback
- [ ] WebP images work or have fallback
- [ ] Intersection Observer works (for lazy loading)
- [ ] No browser-specific console errors

---

## User Experience

### Navigation & Usability

**Global Navigation**
- [ ] Logo links to homepage
- [ ] Main navigation accessible from all pages
- [ ] Active page indicated in navigation
- [ ] Mobile menu works (hamburger icon if applicable)
- [ ] Footer navigation works
- [ ] Footer links valid and working

**Blog Navigation**
- [ ] Breadcrumbs present and functional
- [ ] "Back to blog" link on post pages
- [ ] Category filter intuitive and works
- [ ] Related posts relevant and clickable
- [ ] Pagination works (if implemented)
- [ ] Search works (if implemented)

**Content Discovery**
- [ ] Latest posts visible on homepage or blog index
- [ ] Categories clearly displayed
- [ ] Tags help discover related content
- [ ] Related posts algorithm works well
- [ ] Breadcrumbs help navigation

**Reading Experience**
- [ ] Typography comfortable to read
- [ ] Line length not too long (50-75 characters)
- [ ] Line height adequate (1.5-1.7)
- [ ] Sufficient contrast
- [ ] No distracting animations
- [ ] Table of contents helpful for long posts
- [ ] Smooth scrolling to headings
- [ ] Share buttons accessible but not intrusive

**Interactive Elements**
- [ ] Buttons have hover/active states
- [ ] Links have hover states
- [ ] Click targets adequate size
- [ ] No accidental clicks (spacing adequate)
- [ ] Loading states present (if needed)
- [ ] Error states helpful

**Mobile Experience**
- [ ] Touch targets adequate size (44x44px minimum)
- [ ] No hover-dependent interactions
- [ ] Tap to expand works as expected
- [ ] Pinch to zoom works on images
- [ ] No tiny text (minimum 16px)
- [ ] Forms usable on mobile (if present)

**Content Quality**
- [ ] Images relevant and high quality
- [ ] No broken images
- [ ] Videos work (if present)
- [ ] Code examples readable and copyable
- [ ] Lists and tables formatted properly
- [ ] Blockquotes styled distinctly

---

## Social Sharing

### Share Functionality

**Share Buttons Present**
- [ ] Twitter share button
- [ ] Facebook share button
- [ ] LinkedIn share button
- [ ] Copy link button

**Twitter Sharing**
- [ ] Click Twitter button opens share dialog
- [ ] Post title pre-filled
- [ ] Post URL included
- [ ] Hashtags included (if applicable)
- [ ] Twitter Card displays correctly in preview
- [ ] Image displays in Twitter Card

**Facebook Sharing**
- [ ] Click Facebook button opens share dialog
- [ ] Post title appears
- [ ] Post description appears
- [ ] Featured image appears
- [ ] URL correct

Test with [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/):
- [ ] No errors or warnings
- [ ] Image displays correctly
- [ ] Title and description correct

**LinkedIn Sharing**
- [ ] Click LinkedIn button opens share dialog
- [ ] Post title appears
- [ ] Post description appears
- [ ] Featured image appears
- [ ] URL correct

**Copy Link**
- [ ] Click copy link button copies URL to clipboard
- [ ] Visual feedback shown (success message/icon)
- [ ] Copied URL correct and complete
- [ ] Fallback for browsers without clipboard API

**Native Share (Mobile)**
- [ ] Native share menu available on mobile (if implemented)
- [ ] Share sheet includes common apps
- [ ] Share data correct (title, text, URL)

---

## Final Production Checklist

### Pre-Launch

- [ ] All environment variables set in production
- [ ] Database migrations run (if applicable)
- [ ] All sample/test content removed or published
- [ ] Analytics tracking code active
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Backup strategy in place
- [ ] SSL certificate valid
- [ ] Custom domain configured
- [ ] DNS records correct and propagated

### Launch Verification

- [ ] Production URL accessible
- [ ] All pages load without errors
- [ ] Performance metrics meet targets (<3s page load)
- [ ] SEO setup complete
- [ ] Analytics tracking confirmed
- [ ] Mobile responsive verified
- [ ] Cross-browser testing complete
- [ ] Accessibility checked
- [ ] Security headers present

### Post-Launch Monitoring

- [ ] Monitor analytics for traffic
- [ ] Check error logs for issues
- [ ] Monitor performance metrics
- [ ] Submit sitemap to search engines
- [ ] Set up uptime monitoring
- [ ] Monitor Core Web Vitals in Search Console
- [ ] Check mobile usability in Search Console
- [ ] Monitor search rankings (optional)

---

## Issue Tracking

Use this section to track any issues found during QA:

### Critical Issues (Must Fix Before Launch)

| # | Issue | Page/Component | Browser/Device | Assigned To | Status |
|---|-------|----------------|----------------|-------------|--------|
| 1 | | | | | |
| 2 | | | | | |

### High Priority (Should Fix Before Launch)

| # | Issue | Page/Component | Browser/Device | Assigned To | Status |
|---|-------|----------------|----------------|-------------|--------|
| 1 | | | | | |
| 2 | | | | | |

### Medium Priority (Nice to Fix)

| # | Issue | Page/Component | Browser/Device | Assigned To | Status |
|---|-------|----------------|----------------|-------------|--------|
| 1 | | | | | |
| 2 | | | | | |

### Low Priority / Enhancement Requests

| # | Issue | Page/Component | Browser/Device | Assigned To | Status |
|---|-------|----------------|----------------|-------------|--------|
| 1 | | | | | |
| 2 | | | | | |

---

## Sign-Off

**QA Testing Complete:** ☐

**Tested By:** _________________
**Date:** _________________
**Signature:** _________________

**Product Owner Approval:** ☐

**Approved By:** _________________
**Date:** _________________
**Signature:** _________________

---

## Additional Notes

Use this space for any additional observations, recommendations, or context:

```
[Add notes here]
```

---

## Related Documentation

- [README.md](../../README.md) - Project overview and setup
- [BLOG_CONTENT_WORKFLOW.md](../guides/BLOG_CONTENT_WORKFLOW.md) - Content publishing workflow
- [BLOG_DEPLOYMENT.md](../guides/BLOG_DEPLOYMENT.md) - Deployment instructions
- [BLOG_DOMAIN_SETUP.md](../guides/BLOG_DOMAIN_SETUP.md) - Custom domain configuration
- [BLOG_STRUCTURED_DATA_VERIFICATION.md](./BLOG_STRUCTURED_DATA_VERIFICATION.md) - SEO structured data validation

---

## Testing Tools Reference

### Performance
- [Google PageSpeed Insights](https://pagespeed.web.dev/)
- [Lighthouse](https://developer.chrome.com/docs/lighthouse/)
- [WebPageTest](https://www.webpagetest.org/)

### SEO
- [Google Search Console](https://search.google.com/search-console/)
- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Schema Markup Validator](https://validator.schema.org/)
- [Open Graph Debugger](https://www.opengraph.xyz/)
- [Twitter Card Validator](https://cards-dev.twitter.com/validator)
- [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)

### Accessibility
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE](https://wave.webaim.org/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

### Security
- [SSL Labs](https://www.ssllabs.com/ssltest/)
- [Security Headers](https://securityheaders.com/)
- [Mozilla Observatory](https://observatory.mozilla.org/)

### Cross-Browser Testing
- [BrowserStack](https://www.browserstack.com/)
- [Sauce Labs](https://saucelabs.com/)
- [LambdaTest](https://www.lambdatest.com/)

### Mobile Testing
- Chrome DevTools Device Mode
- Safari Responsive Design Mode
- Firefox Responsive Design Mode
- Real device testing (recommended)
