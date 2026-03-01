/**
 * Blog API Layer
 * Provides a clean, type-safe interface for fetching blog content
 * Wraps the CMS layer with error handling, caching, and enhanced features
 */

import {
  getAllPosts,
  getAllPostsMeta,
  getPostBySlug,
  getPostsByCategory,
  getPostsByTag,
  getAllCategories,
  getAllTags,
  getRelatedPosts,
  getRecentPosts,
  hasContent,
} from './cms';
import type { BlogPost, BlogPostMeta, Category, Tag } from './types';

/**
 * Pagination options
 */
export interface PaginationOptions {
  page?: number;
  limit?: number;
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

/**
 * Search options
 */
export interface SearchOptions {
  query: string;
  category?: string;
  tag?: string;
  limit?: number;
}

/**
 * API response wrapper for error handling
 */
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

/**
 * Get all blog posts with optional pagination
 * @param options - Pagination options
 * @returns Paginated blog posts
 */
export async function fetchAllPosts(
  options: PaginationOptions = {}
): Promise<PaginatedResponse<BlogPost>> {
  try {
    const { page = 1, limit = 10 } = options;
    const allPosts = getAllPosts();

    // Calculate pagination
    const total = allPosts.length;
    const totalPages = Math.ceil(total / limit);
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;

    // Slice posts for current page
    const paginatedPosts = allPosts.slice(startIndex, endIndex);

    return {
      data: paginatedPosts,
      pagination: {
        page,
        limit,
        total,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1,
      },
    };
  } catch (error) {
    throw new Error(`Failed to fetch posts: ${error}`);
  }
}

/**
 * Get all blog post metadata with optional pagination
 * @param options - Pagination options
 * @returns Paginated blog post metadata
 */
export async function fetchAllPostsMeta(
  options: PaginationOptions = {}
): Promise<PaginatedResponse<BlogPostMeta>> {
  try {
    const { page = 1, limit = 10 } = options;
    const allPosts = getAllPostsMeta();

    // Calculate pagination
    const total = allPosts.length;
    const totalPages = Math.ceil(total / limit);
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;

    // Slice posts for current page
    const paginatedPosts = allPosts.slice(startIndex, endIndex);

    return {
      data: paginatedPosts,
      pagination: {
        page,
        limit,
        total,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1,
      },
    };
  } catch (error) {
    throw new Error(`Failed to fetch post metadata: ${error}`);
  }
}

/**
 * Get a single blog post by slug
 * @param slug - The post slug
 * @returns API response with blog post or error
 */
export async function fetchPost(slug: string): Promise<APIResponse<BlogPost>> {
  try {
    const post = getPostBySlug(slug);

    if (!post) {
      return {
        success: false,
        error: `Post with slug "${slug}" not found`,
      };
    }

    if (!post.published) {
      return {
        success: false,
        error: 'Post is not published',
      };
    }

    return {
      success: true,
      data: post,
    };
  } catch (error) {
    return {
      success: false,
      error: `Failed to fetch post: ${error}`,
    };
  }
}

/**
 * Get posts by category with optional pagination
 * @param categorySlug - The category slug
 * @param options - Pagination options
 * @returns Paginated posts in category
 */
export async function fetchPostsByCategory(
  categorySlug: string,
  options: PaginationOptions = {}
): Promise<PaginatedResponse<BlogPost>> {
  try {
    const { page = 1, limit = 10 } = options;
    const allPosts = getPostsByCategory(categorySlug);

    // Calculate pagination
    const total = allPosts.length;
    const totalPages = Math.ceil(total / limit);
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;

    // Slice posts for current page
    const paginatedPosts = allPosts.slice(startIndex, endIndex);

    return {
      data: paginatedPosts,
      pagination: {
        page,
        limit,
        total,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1,
      },
    };
  } catch (error) {
    throw new Error(`Failed to fetch posts by category: ${error}`);
  }
}

/**
 * Get posts by tag with optional pagination
 * @param tagSlug - The tag slug
 * @param options - Pagination options
 * @returns Paginated posts with tag
 */
export async function fetchPostsByTag(
  tagSlug: string,
  options: PaginationOptions = {}
): Promise<PaginatedResponse<BlogPost>> {
  try {
    const { page = 1, limit = 10 } = options;
    const allPosts = getPostsByTag(tagSlug);

    // Calculate pagination
    const total = allPosts.length;
    const totalPages = Math.ceil(total / limit);
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;

    // Slice posts for current page
    const paginatedPosts = allPosts.slice(startIndex, endIndex);

    return {
      data: paginatedPosts,
      pagination: {
        page,
        limit,
        total,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1,
      },
    };
  } catch (error) {
    throw new Error(`Failed to fetch posts by tag: ${error}`);
  }
}

/**
 * Get all categories
 * @returns Array of categories with post counts
 */
export async function fetchCategories(): Promise<Category[]> {
  try {
    return getAllCategories();
  } catch (error) {
    throw new Error(`Failed to fetch categories: ${error}`);
  }
}

/**
 * Get all tags
 * @returns Array of tags with post counts
 */
export async function fetchTags(): Promise<Tag[]> {
  try {
    return getAllTags();
  } catch (error) {
    throw new Error(`Failed to fetch tags: ${error}`);
  }
}

/**
 * Get related posts for a given post
 * @param slug - The post slug
 * @param limit - Maximum number of related posts (default: 3)
 * @returns Array of related posts
 */
export async function fetchRelatedPosts(
  slug: string,
  limit = 3
): Promise<BlogPost[]> {
  try {
    return getRelatedPosts(slug, limit);
  } catch (error) {
    throw new Error(`Failed to fetch related posts: ${error}`);
  }
}

/**
 * Get recent posts
 * @param limit - Maximum number of posts (default: 5)
 * @returns Array of recent posts
 */
export async function fetchRecentPosts(limit = 5): Promise<BlogPost[]> {
  try {
    return getRecentPosts(limit);
  } catch (error) {
    throw new Error(`Failed to fetch recent posts: ${error}`);
  }
}

/**
 * Search posts by title, description, or content
 * @param options - Search options
 * @returns Array of matching posts
 */
export async function searchPosts(
  options: SearchOptions
): Promise<BlogPost[]> {
  try {
    const { query, category, tag, limit = 10 } = options;

    // Get base set of posts
    let posts = getAllPosts();

    // Filter by category if specified
    if (category) {
      posts = posts.filter(
        (post) => post.category.toLowerCase() === category.toLowerCase()
      );
    }

    // Filter by tag if specified
    if (tag) {
      posts = posts.filter((post) =>
        post.tags.some((t) => t.toLowerCase() === tag.toLowerCase())
      );
    }

    // Search in title, description, and content
    const searchQuery = query.toLowerCase();
    const results = posts.filter(
      (post) =>
        post.title.toLowerCase().includes(searchQuery) ||
        post.description.toLowerCase().includes(searchQuery) ||
        post.content.toLowerCase().includes(searchQuery)
    );

    return results.slice(0, limit);
  } catch (error) {
    throw new Error(`Failed to search posts: ${error}`);
  }
}

/**
 * Check if blog has content
 * @returns True if blog has at least one published post
 */
export async function checkHasContent(): Promise<boolean> {
  try {
    return hasContent();
  } catch (error) {
    return false;
  }
}

/**
 * Get blog statistics
 * @returns Blog statistics (post count, category count, tag count)
 */
export async function fetchBlogStats(): Promise<{
  totalPosts: number;
  totalCategories: number;
  totalTags: number;
  recentPostsCount: number;
}> {
  try {
    const posts = getAllPosts();
    const categories = getAllCategories();
    const tags = getAllTags();
    const recentPosts = getRecentPosts(5);

    return {
      totalPosts: posts.length,
      totalCategories: categories.length,
      totalTags: tags.length,
      recentPostsCount: recentPosts.length,
    };
  } catch (error) {
    throw new Error(`Failed to fetch blog stats: ${error}`);
  }
}

/**
 * Validate post slug format
 * @param slug - The slug to validate
 * @returns True if slug is valid
 */
export function isValidSlug(slug: string): boolean {
  // Slug should be lowercase, alphanumeric with hyphens
  const slugPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
  return slugPattern.test(slug);
}

/**
 * Generate slug from title
 * @param title - The post title
 * @returns URL-safe slug
 */
export function generateSlug(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Replace multiple hyphens with single hyphen
    .replace(/^-+|-+$/g, ''); // Remove leading/trailing hyphens
}
