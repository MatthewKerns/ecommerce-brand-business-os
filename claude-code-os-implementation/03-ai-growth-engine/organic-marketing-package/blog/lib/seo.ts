/**
 * SEO Utilities
 * Helper functions for generating meta tags, Open Graph tags, and structured data
 * Ensures consistent SEO implementation across blog pages
 */

import type { Metadata } from 'next';
import type { BlogPost } from './types';

/**
 * Base URL for the blog
 * Should be updated to production URL when deployed
 */
const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || 'https://infinitycards.com';
const BLOG_URL = `${BASE_URL}/blog`;

/**
 * Default site metadata
 */
const SITE_NAME = 'InfinityCards Blog';
const SITE_DESCRIPTION = 'Expert insights on custom playing cards, print-on-demand, and e-commerce strategies';
const DEFAULT_IMAGE = `${BASE_URL}/og-image.jpg`;

/**
 * Generate canonical URL for a blog post
 * @param slug - The post slug
 * @returns Full canonical URL
 */
export function getCanonicalUrl(slug: string): string {
  return `${BLOG_URL}/${slug}`;
}

/**
 * Generate Open Graph image URL
 * @param image - Optional custom image URL
 * @returns Full image URL
 */
export function getOGImageUrl(image?: string): string {
  if (!image) return DEFAULT_IMAGE;

  // If image is already a full URL, return as-is
  if (image.startsWith('http://') || image.startsWith('https://')) {
    return image;
  }

  // Otherwise, construct full URL
  return `${BASE_URL}${image.startsWith('/') ? '' : '/'}${image}`;
}

/**
 * Generate SEO-optimized metadata for a blog post
 * @param post - Blog post data
 * @returns Next.js Metadata object
 */
export function generatePostMetadata(post: BlogPost): Metadata {
  const title = `${post.title} - ${SITE_NAME}`;
  const description = post.description;
  const canonical = getCanonicalUrl(post.slug);
  const imageUrl = getOGImageUrl(post.image);
  const publishedTime = new Date(post.date).toISOString();

  return {
    title,
    description,
    authors: [{ name: post.author }],
    keywords: post.tags.join(', '),
    category: post.category,
    alternates: {
      canonical,
    },
    openGraph: {
      title: post.title,
      description,
      url: canonical,
      siteName: SITE_NAME,
      locale: 'en_US',
      type: 'article',
      publishedTime,
      authors: [post.author],
      tags: post.tags,
      images: [
        {
          url: imageUrl,
          width: 1200,
          height: 630,
          alt: post.title,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description,
      images: [imageUrl],
      creator: '@infinitycards', // Update with actual Twitter handle
    },
    robots: {
      index: post.published,
      follow: post.published,
      googleBot: {
        index: post.published,
        follow: post.published,
      },
    },
  };
}

/**
 * Generate SEO-optimized metadata for blog home page
 * @param options - Optional metadata overrides
 * @returns Next.js Metadata object
 */
export function generateBlogHomeMetadata(options?: {
  title?: string;
  description?: string;
}): Metadata {
  const title = options?.title || SITE_NAME;
  const description = options?.description || SITE_DESCRIPTION;

  return {
    title,
    description,
    alternates: {
      canonical: BLOG_URL,
    },
    openGraph: {
      title,
      description,
      url: BLOG_URL,
      siteName: SITE_NAME,
      locale: 'en_US',
      type: 'website',
      images: [
        {
          url: DEFAULT_IMAGE,
          width: 1200,
          height: 630,
          alt: SITE_NAME,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: [DEFAULT_IMAGE],
      creator: '@infinitycards', // Update with actual Twitter handle
    },
  };
}

/**
 * Generate JSON-LD structured data for a blog post
 * @param post - Blog post data
 * @returns JSON-LD structured data object
 */
export function generateBlogPostStructuredData(post: BlogPost) {
  const imageUrl = getOGImageUrl(post.image);
  const canonical = getCanonicalUrl(post.slug);

  return {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.title,
    description: post.description,
    image: imageUrl,
    datePublished: new Date(post.date).toISOString(),
    dateModified: new Date(post.date).toISOString(), // Update if you track modification dates
    author: {
      '@type': 'Person',
      name: post.author,
    },
    publisher: {
      '@type': 'Organization',
      name: 'InfinityCards',
      logo: {
        '@type': 'ImageObject',
        url: `${BASE_URL}/logo.png`,
      },
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': canonical,
    },
    keywords: post.tags.join(', '),
    articleSection: post.category,
    wordCount: estimateWordCount(post.content),
    timeRequired: `PT${post.readingTime}M`,
  };
}

/**
 * Generate JSON-LD structured data for breadcrumbs
 * @param post - Blog post data
 * @returns JSON-LD breadcrumb structured data
 */
export function generateBreadcrumbStructuredData(post: BlogPost) {
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
        name: post.title,
        item: getCanonicalUrl(post.slug),
      },
    ],
  };
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
 * Truncate description to optimal length for meta tags
 * @param description - Original description
 * @param maxLength - Maximum character length (default: 155)
 * @returns Truncated description
 */
export function truncateDescription(
  description: string,
  maxLength = 155
): string {
  if (description.length <= maxLength) {
    return description;
  }

  // Find last complete word within maxLength
  const truncated = description.substring(0, maxLength);
  const lastSpace = truncated.lastIndexOf(' ');

  if (lastSpace > 0) {
    return `${truncated.substring(0, lastSpace)}...`;
  }

  return `${truncated}...`;
}

/**
 * Generate meta robots tag content
 * @param published - Whether the post is published
 * @returns Robots meta tag content
 */
export function getMetaRobots(published: boolean): string {
  return published ? 'index, follow' : 'noindex, nofollow';
}
