import { Suspense } from "react";
import { getAllPostsMeta, getAllCategories } from "@/lib/cms";
import { BlogCard } from "@/components/BlogCard";
import { CategoryFilter } from "@/components/CategoryFilter";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Blog - InfinityCards",
  description:
    "Discover expert insights on Magic: The Gathering, tournament prep, deck building, and card care from the InfinityCards team.",
};

interface BlogPageProps {
  searchParams: {
    category?: string;
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

export default function BlogPage({ searchParams }: BlogPageProps) {
  // Get all posts and categories
  const allPosts = getAllPostsMeta();
  const categories = getAllCategories();

  // Filter posts by category if specified
  const selectedCategory = searchParams.category;
  const filteredPosts = selectedCategory
    ? allPosts.filter(
        (post) => post.category.toLowerCase() === selectedCategory.toLowerCase()
      )
    : allPosts;

  return (
    <div className="container mx-auto px-4 py-12">
      {/* Header */}
      <div className="mb-12 text-center">
        <h1 className="mb-4 text-4xl font-bold text-gray-900 md:text-5xl">
          InfinityCards Blog
        </h1>
        <p className="mx-auto max-w-2xl text-lg text-gray-600">
          Expert insights on Magic: The Gathering, tournament strategies, deck
          building tips, and everything you need to elevate your game.
        </p>
      </div>

      {/* Category Filter */}
      <Suspense fallback={<div className="mb-8 h-24 animate-pulse rounded-lg bg-gray-100" />}>
        <CategoryFilter categories={categories} />
      </Suspense>

      {/* Posts Grid */}
      <Suspense fallback={<BlogPostsLoading />}>
        {filteredPosts.length === 0 ? (
          <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
            <h2 className="mb-2 text-2xl font-semibold text-gray-900">
              No posts found
            </h2>
            <p className="text-gray-600">
              {selectedCategory
                ? `No posts in the "${selectedCategory}" category yet.`
                : "No blog posts available yet. Check back soon!"}
            </p>
          </div>
        ) : (
          <>
            {/* Results count */}
            <div className="mb-6 flex items-center justify-between">
              <p className="text-sm text-gray-600">
                {filteredPosts.length}{" "}
                {filteredPosts.length === 1 ? "post" : "posts"}
                {selectedCategory && (
                  <span>
                    {" "}
                    in{" "}
                    <span className="font-semibold">
                      {selectedCategory
                        .split("-")
                        .map(
                          (word) =>
                            word.charAt(0).toUpperCase() + word.slice(1)
                        )
                        .join(" ")}
                    </span>
                  </span>
                )}
              </p>
            </div>

            {/* Posts grid */}
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {filteredPosts.map((post) => (
                <BlogCard key={post.slug} post={post} />
              ))}
            </div>
          </>
        )}
      </Suspense>
    </div>
  );
}
