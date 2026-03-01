/**
 * TypeScript types for blog platform
 * Defines data structures for blog posts, categories, and metadata
 */

export interface BlogPostFrontmatter {
  title: string;
  description: string;
  date: string;
  category: string;
  tags?: string[];
  author?: string;
  image?: string;
  published?: boolean;
}

export interface BlogPost {
  slug: string;
  title: string;
  description: string;
  date: string;
  category: string;
  tags: string[];
  author: string;
  image?: string;
  content: string;
  readingTime: number; // in minutes
  published: boolean;
}

export interface BlogPostMeta {
  slug: string;
  title: string;
  description: string;
  date: string;
  category: string;
  tags: string[];
  author: string;
  image?: string;
  readingTime: number;
  published: boolean;
}

export interface Category {
  name: string;
  slug: string;
  description: string;
  count: number;
}

export interface Tag {
  name: string;
  slug: string;
  count: number;
}

export interface Author {
  name: string;
  slug: string;
  bio?: string;
  avatar?: string;
}
