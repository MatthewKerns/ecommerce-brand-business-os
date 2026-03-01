import { notFound } from "next/navigation";
import Link from "next/link";
import { Suspense } from "react";
import {
  getPostsByCategory,
  getAllCategories,
  getAllPostsMeta,
} from "@/lib/cms";
import { BlogCard } from "@/components/BlogCard";
import type { Metadata } from "next";

interface CategoryPageProps {
  params: {
    category: string;
  };
}

// Generate static params for all categories at build time
export async function generateStaticParams() {
  const categories = getAllCategories();
  return categories.map((category) => ({
    category: category.slug,
  }));
}

// Generate metadata for SEO
export async function generateMetadata({
  params,
}: CategoryPageProps): Promise<Metadata> {
  const { category: categorySlug } = params;
  const categories = getAllCategories();
  const category = categories.find((cat) => cat.slug === categorySlug);

  if (!category) {
    return {
      title: "Category Not Found - InfinityCards Blog",
    };
  }

  return {
    title: `${category.name} - InfinityCards Blog`,
    description: `Browse all ${category.name} articles on the InfinityCards blog. Expert insights and tips for Magic: The Gathering players.`,
    openGraph: {
      title: `${category.name} - InfinityCards Blog`,
      description: `Browse all ${category.name} articles on the InfinityCards blog. Expert insights and tips for Magic: The Gathering players.`,
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: `${category.name} - InfinityCards Blog`,
      description: `Browse all ${category.name} articles on the InfinityCards blog. Expert insights and tips for Magic: The Gathering players.`,
    },
  };
}

// Loading component for Suspense
function BlogPostsLoading() {
  return (
    <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="h-96 animate-pulse rounded-lg border border-gray-200 bg-gray-100"
        />
      ))}
    </div>
  );
}

export default function CategoryPage({ params }: CategoryPageProps) {
  const { category: categorySlug } = params;

  // Get category information
  const categories = getAllCategories();
  const category = categories.find((cat) => cat.slug === categorySlug);

  // If category doesn't exist, show 404
  if (!category) {
    notFound();
  }

  // Get all posts in this category
  const posts = getAllPostsMeta().filter(
    (post) => post.category.toLowerCase() === categorySlug.toLowerCase()
  );

  // Get category description based on slug
  const getCategoryDescription = (slug: string): string => {
    const descriptions: Record<string, string> = {
      "tournament-prep":
        "Master the art of tournament preparation with expert strategies, mental preparation techniques, and competitive play insights to elevate your game.",
      "deck-building":
        "Discover advanced deck building strategies, card synergies, and meta analysis to create powerful and competitive decks.",
      "card-care":
        "Learn how to protect and preserve your valuable Magic: The Gathering cards with proper storage, handling, and maintenance techniques.",
      strategy:
        "Dive deep into gameplay strategies, tactical decisions, and winning techniques to improve your Magic: The Gathering skills.",
      guides:
        "Comprehensive guides covering all aspects of Magic: The Gathering, from beginner basics to advanced play.",
      news: "Stay updated with the latest Magic: The Gathering news, product releases, and community updates.",
    };

    return (
      descriptions[slug] ||
      `Explore all ${category.name} articles and insights from the InfinityCards blog.`
    );
  };

  const categoryDescription = getCategoryDescription(categorySlug);

  return (
    <div className="container mx-auto px-4 py-12">
      {/* Breadcrumb Navigation */}
      <nav className="mb-8 flex items-center space-x-2 text-sm text-gray-600">
        <Link
          href="/"
          className="hover:text-primary transition-colors"
        >
          Home
        </Link>
        <span className="text-gray-400">/</span>
        <Link
          href="/blog"
          className="hover:text-primary transition-colors"
        >
          Blog
        </Link>
        <span className="text-gray-400">/</span>
        <span className="font-medium text-gray-900">{category.name}</span>
      </nav>

      {/* Category Header */}
      <div className="mb-12">
        <div className="mb-4 inline-flex items-center rounded-full bg-primary/10 px-4 py-2">
          <span className="text-sm font-semibold uppercase tracking-wider text-primary">
            Category
          </span>
        </div>
        <h1 className="mb-4 text-4xl font-bold text-gray-900 md:text-5xl">
          {category.name}
        </h1>
        <p className="max-w-3xl text-lg text-gray-600">
          {categoryDescription}
        </p>
        <div className="mt-4 text-sm text-gray-500">
          {category.count} {category.count === 1 ? "article" : "articles"}
        </div>
      </div>

      {/* Posts Grid */}
      <Suspense fallback={<BlogPostsLoading />}>
        {posts.length === 0 ? (
          <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
            <h2 className="mb-2 text-2xl font-semibold text-gray-900">
              No posts found
            </h2>
            <p className="mb-6 text-gray-600">
              No posts in the &quot;{category.name}&quot; category yet. Check
              back soon!
            </p>
            <Link
              href="/blog"
              className="inline-block rounded-lg bg-primary px-6 py-3 text-white transition-colors hover:bg-primary/90"
            >
              Browse All Posts
            </Link>
          </div>
        ) : (
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {posts.map((post) => (
              <BlogCard key={post.slug} post={post} />
            ))}
          </div>
        )}
      </Suspense>

      {/* Back to Blog Link */}
      <div className="mt-12 text-center">
        <Link
          href="/blog"
          className="inline-flex items-center text-primary hover:underline"
        >
          ← Back to all posts
        </Link>
      </div>
    </div>
  );
}
