/**
 * Structured Data Utilities
 * Generates Schema.org JSON-LD markup for enhanced SEO and rich results
 * Supports Article, BreadcrumbList, WebSite, and Organization schemas
 */

import type { BlogPost } from './types';

/**
 * Base URL for the blog
 * Should be updated to production URL when deployed
 */
const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || 'https://infinitycards.com';
const BLOG_URL = `${BASE_URL}/blog`;

/**
 * Organization information for Schema.org markup
 */
const ORGANIZATION = {
  name: 'InfinityCards',
  url: BASE_URL,
  logo: `${BASE_URL}/logo.png`,
  description: 'Custom playing cards and print-on-demand solutions',
  sameAs: [
    'https://twitter.com/infinitycards',
    'https://facebook.com/infinitycards',
    'https://linkedin.com/company/infinitycards',
  ],
};

/**
 * Get full canonical URL for a blog post
 * @param slug - The post slug
 * @returns Full canonical URL
 */
function getCanonicalUrl(slug: string): string {
  return `${BLOG_URL}/${slug}`;
}

/**
 * Get full image URL
 * @param image - Optional custom image URL or path
 * @returns Full image URL
 */
function getImageUrl(image?: string): string {
  if (!image) return `${BASE_URL}/og-image.jpg`;

  // If image is already a full URL, return as-is
  if (image.startsWith('http://') || image.startsWith('https://')) {
    return image;
  }

  // Otherwise, construct full URL
  return `${BASE_URL}${image.startsWith('/') ? '' : '/'}${image}`;
}

/**
 * Estimate word count from content
 * @param content - Post content
 * @returns Estimated word count
 */
function estimateWordCount(content: string): number {
  return content.split(/\s+/).filter((word) => word.length > 0).length;
}

/**
 * Generate Article schema (Schema.org)
 * Enhanced version with all recommended properties for rich results
 * @param post - Blog post data
 * @returns Article structured data object
 */
export function generateArticleSchema(post: BlogPost) {
  const imageUrl = getImageUrl(post.image);
  const canonical = getCanonicalUrl(post.slug);
  const wordCount = estimateWordCount(post.content);

  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    '@id': canonical,
    headline: post.title,
    description: post.description,
    image: {
      '@type': 'ImageObject',
      url: imageUrl,
      width: 1200,
      height: 630,
    },
    datePublished: new Date(post.date).toISOString(),
    dateModified: new Date(post.date).toISOString(),
    author: {
      '@type': 'Person',
      name: post.author,
      url: `${BASE_URL}/about`,
    },
    publisher: {
      '@type': 'Organization',
      name: ORGANIZATION.name,
      url: ORGANIZATION.url,
      logo: {
        '@type': 'ImageObject',
        url: ORGANIZATION.logo,
        width: 600,
        height: 60,
      },
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': canonical,
    },
    keywords: post.tags.join(', '),
    articleSection: post.category,
    wordCount,
    timeRequired: `PT${post.readingTime}M`,
    inLanguage: 'en-US',
    isAccessibleForFree: true,
  };
}

/**
 * Generate BlogPosting schema (Schema.org)
 * Alternative to Article schema, more specific for blog posts
 * @param post - Blog post data
 * @returns BlogPosting structured data object
 */
export function generateBlogPostingSchema(post: BlogPost) {
  const articleSchema = generateArticleSchema(post);

  return {
    ...articleSchema,
    '@type': 'BlogPosting',
  };
}

/**
 * Generate BreadcrumbList schema (Schema.org)
 * Helps search engines understand site hierarchy
 * @param post - Blog post data
 * @returns BreadcrumbList structured data object
 */
export function generateBreadcrumbSchema(post: BlogPost) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: 'Home',
        item: BASE_URL,
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: 'Blog',
        item: BLOG_URL,
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: post.category,
        item: `${BLOG_URL}/category/${post.category.toLowerCase().replace(/\s+/g, '-')}`,
      },
      {
        '@type': 'ListItem',
        position: 4,
        name: post.title,
        item: getCanonicalUrl(post.slug),
      },
    ],
  };
}

/**
 * Generate WebSite schema (Schema.org)
 * Should be included on the blog home page
 * @returns WebSite structured data object
 */
export function generateWebSiteSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': `${BASE_URL}/#website`,
    url: BASE_URL,
    name: ORGANIZATION.name,
    description: ORGANIZATION.description,
    publisher: {
      '@id': `${BASE_URL}/#organization`,
    },
    inLanguage: 'en-US',
  };
}

/**
 * Generate Organization schema (Schema.org)
 * Should be included on the blog home page
 * @returns Organization structured data object
 */
export function generateOrganizationSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    '@id': `${BASE_URL}/#organization`,
    name: ORGANIZATION.name,
    url: ORGANIZATION.url,
    logo: {
      '@type': 'ImageObject',
      url: ORGANIZATION.logo,
      width: 600,
      height: 60,
    },
    description: ORGANIZATION.description,
    sameAs: ORGANIZATION.sameAs,
  };
}

/**
 * Generate category page BreadcrumbList schema
 * @param category - Category name
 * @returns BreadcrumbList structured data object
 */
export function generateCategoryBreadcrumbSchema(category: string) {
  const categorySlug = category.toLowerCase().replace(/\s+/g, '-');

  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: 'Home',
        item: BASE_URL,
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: 'Blog',
        item: BLOG_URL,
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: category,
        item: `${BLOG_URL}/category/${categorySlug}`,
      },
    ],
  };
}

/**
 * Generate CollectionPage schema for blog index or category pages
 * @param options - Configuration options
 * @returns CollectionPage structured data object
 */
export function generateCollectionPageSchema(options: {
  name: string;
  description: string;
  url: string;
}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    '@id': options.url,
    url: options.url,
    name: options.name,
    description: options.description,
    isPartOf: {
      '@id': `${BASE_URL}/#website`,
    },
    breadcrumb: {
      '@type': 'BreadcrumbList',
      itemListElement: [
        {
          '@type': 'ListItem',
          position: 1,
          name: 'Home',
          item: BASE_URL,
        },
        {
          '@type': 'ListItem',
          position: 2,
          name: 'Blog',
          item: BLOG_URL,
        },
      ],
    },
  };
}
