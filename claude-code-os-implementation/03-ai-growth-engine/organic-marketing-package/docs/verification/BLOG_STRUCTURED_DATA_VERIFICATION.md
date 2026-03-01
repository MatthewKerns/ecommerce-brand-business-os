# Structured Data Verification

This document provides information on how to verify the Schema.org structured data implementation for the blog.

## What Was Implemented

The blog now includes comprehensive Schema.org JSON-LD structured data for enhanced SEO and rich results in search engines.

### Article Schema

Each blog post includes an `Article` schema with the following properties:

**Required Properties (for Google Rich Results):**
- ✅ `headline`: Post title
- ✅ `author`: Person schema with author name
- ✅ `datePublished`: ISO 8601 format publication date
- ✅ `image`: ImageObject with URL and dimensions

**Additional Recommended Properties:**
- `description`: Post description
- `dateModified`: Last modification date
- `publisher`: Organization schema with logo
- `mainEntityOfPage`: WebPage reference
- `keywords`: Comma-separated tags
- `articleSection`: Post category
- `wordCount`: Estimated word count
- `timeRequired`: Reading time in ISO 8601 duration format
- `inLanguage`: Content language (en-US)
- `isAccessibleForFree`: Accessibility flag

### BreadcrumbList Schema

Navigation breadcrumbs are provided to help search engines understand site hierarchy:
- Home → Blog → Category → Post Title

## How to Verify

### 1. Google Rich Results Test

**URL:** https://search.google.com/test/rich-results

**Steps:**
1. Visit the Rich Results Test tool
2. Enter your blog post URL (e.g., `https://infinitycards.com/blog/your-post-slug`)
3. Click "Test URL"
4. Wait for analysis to complete

**Expected Results:**
- ✅ "Article" schema detected
- ✅ No errors or warnings
- ✅ Preview shows: headline, author, date published, image
- ✅ Rich result preview displays correctly

### 2. Schema Markup Validator

**URL:** https://validator.schema.org/

**Steps:**
1. Visit the Schema.org validator
2. Enter your blog post URL or paste the HTML
3. Click "Validate"

**Expected Results:**
- ✅ No errors
- ✅ Article type recognized
- ✅ BreadcrumbList type recognized
- ✅ All required properties present

### 3. Manual Inspection

**Steps:**
1. Visit any blog post on your site
2. Open browser developer tools (F12)
3. View page source (Ctrl+U or Cmd+U)
4. Search for `application/ld+json`

**Expected Results:**
Two JSON-LD script blocks should be present:

#### Article Schema Example:
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "@id": "https://infinitycards.com/blog/post-slug",
  "headline": "Your Post Title",
  "description": "Post description",
  "image": {
    "@type": "ImageObject",
    "url": "https://infinitycards.com/images/post-image.jpg",
    "width": 1200,
    "height": 630
  },
  "datePublished": "2024-01-01T00:00:00.000Z",
  "dateModified": "2024-01-01T00:00:00.000Z",
  "author": {
    "@type": "Person",
    "name": "Author Name",
    "url": "https://infinitycards.com/about"
  },
  "publisher": {
    "@type": "Organization",
    "name": "InfinityCards",
    "url": "https://infinitycards.com",
    "logo": {
      "@type": "ImageObject",
      "url": "https://infinitycards.com/logo.png",
      "width": 600,
      "height": 60
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://infinitycards.com/blog/post-slug"
  },
  "keywords": "tag1, tag2, tag3",
  "articleSection": "category-name",
  "wordCount": 1500,
  "timeRequired": "PT8M",
  "inLanguage": "en-US",
  "isAccessibleForFree": true
}
```

#### BreadcrumbList Schema Example:
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://infinitycards.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Blog",
      "item": "https://infinitycards.com/blog"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Category Name",
      "item": "https://infinitycards.com/blog/category/category-name"
    },
    {
      "@type": "ListItem",
      "position": 4,
      "name": "Post Title",
      "item": "https://infinitycards.com/blog/post-slug"
    }
  ]
}
```

### 4. Google Search Console

After deployment, monitor structured data in Google Search Console:

**Steps:**
1. Log in to Google Search Console
2. Navigate to "Enhancements" → "Articles"
3. Check for detected articles
4. Monitor for errors or warnings

**Expected Results:**
- ✅ Blog posts appear in "Valid" section
- ✅ No errors in "Error" section
- ✅ Article properties correctly parsed
- ✅ Rich results eligible for display

## Common Issues and Solutions

### Issue: "Missing required property"
**Solution:** Ensure all blog posts have required frontmatter fields (title, description, date, author, image, category, tags)

### Issue: "Invalid date format"
**Solution:** Dates are automatically converted to ISO 8601 format. Ensure date field in frontmatter is valid.

### Issue: "Image URL not accessible"
**Solution:** Verify image paths are correct and images are publicly accessible. Use full URLs for external images.

### Issue: "Publisher logo missing"
**Solution:** Ensure `/logo.png` exists in the public directory with recommended dimensions (600x60px).

## Additional Schema Types Available

The `lib/structuredData.ts` module also provides additional schema generators:

1. **WebSite Schema** - For blog home page
2. **Organization Schema** - For blog home page
3. **CollectionPage Schema** - For category/index pages
4. **Category Breadcrumb Schema** - For category pages

These can be added to other pages as needed for enhanced SEO.

## Testing Checklist

Before marking this subtask as complete:

- [ ] Article schema validates without errors in Google Rich Results Test
- [ ] BreadcrumbList schema validates without errors
- [ ] All required properties are present (headline, author, datePublished, image)
- [ ] Schema appears correctly in page source
- [ ] No JavaScript errors in browser console
- [ ] JSON-LD syntax is valid (no parse errors)
- [ ] Image URLs are absolute and accessible
- [ ] Publisher organization details are correct

## References

- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Schema.org Article](https://schema.org/Article)
- [Schema.org BreadcrumbList](https://schema.org/BreadcrumbList)
- [Google Search Central - Article Structured Data](https://developers.google.com/search/docs/appearance/structured-data/article)
- [Schema.org Validator](https://validator.schema.org/)

## Support

For issues or questions about structured data implementation, refer to:
- `lib/structuredData.ts` - Schema generation functions
- `app/blog/[slug]/page.tsx` - Implementation in blog post pages
- Google Search Console - Post-deployment monitoring
