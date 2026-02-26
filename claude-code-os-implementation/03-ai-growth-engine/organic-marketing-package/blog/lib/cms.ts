/**
 * CMS Integration Layer
 * File-based content management using MDX files stored in content/posts/
 * Provides functions to read, parse, and query blog posts
 */

import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import readingTime from 'reading-time';
import type {
  BlogPost,
  BlogPostMeta,
  BlogPostFrontmatter,
  Category,
  Tag,
} from './types';

const CONTENT_DIR = path.join(process.cwd(), 'content', 'posts');

/**
 * Ensure content directory exists
 */
function ensureContentDirectory(): void {
  if (!fs.existsSync(CONTENT_DIR)) {
    fs.mkdirSync(CONTENT_DIR, { recursive: true });
  }
}

/**
 * Get all MDX/MD files from content directory
 */
function getPostFiles(): string[] {
  ensureContentDirectory();

  if (!fs.existsSync(CONTENT_DIR)) {
    return [];
  }

  const files = fs.readdirSync(CONTENT_DIR);
  return files.filter(
    (file) => file.endsWith('.mdx') || file.endsWith('.md')
  );
}

/**
 * Parse a blog post file and return structured data
 */
function parsePostFile(filename: string): BlogPost | null {
  try {
    const slug = filename.replace(/\.(mdx|md)$/, '');
    const filePath = path.join(CONTENT_DIR, filename);
    const fileContents = fs.readFileSync(filePath, 'utf8');

    const { data, content } = matter(fileContents);
    const frontmatter = data as BlogPostFrontmatter;

    // Calculate reading time
    const stats = readingTime(content);

    // Default values
    const post: BlogPost = {
      slug,
      title: frontmatter.title || 'Untitled',
      description: frontmatter.description || '',
      date: frontmatter.date || new Date().toISOString(),
      category: frontmatter.category || 'uncategorized',
      tags: frontmatter.tags || [],
      author: frontmatter.author || 'InfinityCards Team',
      image: frontmatter.image,
      content,
      readingTime: Math.ceil(stats.minutes),
      published: frontmatter.published !== false, // Default to true
    };

    return post;
  } catch (error) {
    console.error(`Error parsing post file ${filename}:`, error);
    return null;
  }
}

/**
 * Get all blog posts
 * @param includeUnpublished - Whether to include unpublished posts (default: false)
 * @returns Array of blog posts sorted by date (newest first)
 */
export function getAllPosts(includeUnpublished = false): BlogPost[] {
  const files = getPostFiles();
  const posts = files
    .map(parsePostFile)
    .filter((post): post is BlogPost => post !== null)
    .filter((post) => includeUnpublished || post.published)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  return posts;
}

/**
 * Get all blog post metadata (without content)
 * @param includeUnpublished - Whether to include unpublished posts (default: false)
 * @returns Array of blog post metadata sorted by date (newest first)
 */
export function getAllPostsMeta(includeUnpublished = false): BlogPostMeta[] {
  const posts = getAllPosts(includeUnpublished);
  return posts.map(({ content, ...meta }) => meta);
}

/**
 * Get a single blog post by slug
 * @param slug - The post slug
 * @returns Blog post or null if not found
 */
export function getPostBySlug(slug: string): BlogPost | null {
  const filename = `${slug}.mdx`;
  const altFilename = `${slug}.md`;

  if (fs.existsSync(path.join(CONTENT_DIR, filename))) {
    return parsePostFile(filename);
  } else if (fs.existsSync(path.join(CONTENT_DIR, altFilename))) {
    return parsePostFile(altFilename);
  }

  return null;
}

/**
 * Get all posts in a specific category
 * @param categorySlug - The category slug
 * @param includeUnpublished - Whether to include unpublished posts (default: false)
 * @returns Array of blog posts in the category
 */
export function getPostsByCategory(
  categorySlug: string,
  includeUnpublished = false
): BlogPost[] {
  const posts = getAllPosts(includeUnpublished);
  return posts.filter(
    (post) => post.category.toLowerCase() === categorySlug.toLowerCase()
  );
}

/**
 * Get all posts with a specific tag
 * @param tagSlug - The tag slug
 * @param includeUnpublished - Whether to include unpublished posts (default: false)
 * @returns Array of blog posts with the tag
 */
export function getPostsByTag(
  tagSlug: string,
  includeUnpublished = false
): BlogPost[] {
  const posts = getAllPosts(includeUnpublished);
  return posts.filter((post) =>
    post.tags.some((tag) => tag.toLowerCase() === tagSlug.toLowerCase())
  );
}

/**
 * Get all unique categories with post counts
 * @returns Array of categories sorted by count (descending)
 */
export function getAllCategories(): Category[] {
  const posts = getAllPosts();
  const categoryMap = new Map<string, number>();

  posts.forEach((post) => {
    const category = post.category.toLowerCase();
    categoryMap.set(category, (categoryMap.get(category) || 0) + 1);
  });

  const categories: Category[] = Array.from(categoryMap.entries()).map(
    ([slug, count]) => ({
      name: slug
        .split('-')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' '),
      slug,
      description: '', // Can be enhanced with category descriptions later
      count,
    })
  );

  return categories.sort((a, b) => b.count - a.count);
}

/**
 * Get all unique tags with post counts
 * @returns Array of tags sorted by count (descending)
 */
export function getAllTags(): Tag[] {
  const posts = getAllPosts();
  const tagMap = new Map<string, number>();

  posts.forEach((post) => {
    post.tags.forEach((tag) => {
      const tagSlug = tag.toLowerCase();
      tagMap.set(tagSlug, (tagMap.get(tagSlug) || 0) + 1);
    });
  });

  const tags: Tag[] = Array.from(tagMap.entries()).map(([slug, count]) => ({
    name: slug
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' '),
    slug,
    count,
  }));

  return tags.sort((a, b) => b.count - a.count);
}

/**
 * Get related posts based on category and tags
 * @param slug - The current post slug
 * @param limit - Maximum number of related posts to return (default: 3)
 * @returns Array of related blog posts
 */
export function getRelatedPosts(slug: string, limit = 3): BlogPost[] {
  const currentPost = getPostBySlug(slug);
  if (!currentPost) return [];

  const allPosts = getAllPosts();

  // Score posts based on shared category and tags
  const scoredPosts = allPosts
    .filter((post) => post.slug !== slug)
    .map((post) => {
      let score = 0;

      // Same category: +3 points
      if (post.category === currentPost.category) {
        score += 3;
      }

      // Shared tags: +1 point per tag
      const sharedTags = post.tags.filter((tag) =>
        currentPost.tags.includes(tag)
      );
      score += sharedTags.length;

      return { post, score };
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score);

  return scoredPosts.slice(0, limit).map(({ post }) => post);
}

/**
 * Get recent posts
 * @param limit - Maximum number of posts to return (default: 5)
 * @returns Array of recent blog posts
 */
export function getRecentPosts(limit = 5): BlogPost[] {
  const posts = getAllPosts();
  return posts.slice(0, limit);
}

/**
 * Check if content directory exists and has posts
 * @returns True if content directory exists and has at least one post
 */
export function hasContent(): boolean {
  return getPostFiles().length > 0;
}
