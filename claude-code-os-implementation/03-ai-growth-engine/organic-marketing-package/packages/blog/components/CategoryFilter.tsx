"use client";

import { useRouter, useSearchParams } from "next/navigation";
import type { Category } from "@/lib/types";

interface CategoryFilterProps {
  categories: Category[];
}

export function CategoryFilter({ categories }: CategoryFilterProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const selectedCategory = searchParams.get("category");

  const handleCategoryChange = (categorySlug: string | null) => {
    if (categorySlug) {
      router.push(`/blog?category=${categorySlug}`);
    } else {
      router.push("/blog");
    }
  };

  return (
    <div className="mb-8 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">
        Filter by Category
      </h2>

      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => handleCategoryChange(null)}
          className={`rounded-full px-4 py-2 text-sm font-medium transition-colors ${
            !selectedCategory
              ? "bg-primary text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          All Posts
        </button>

        {categories.map((category) => (
          <button
            key={category.slug}
            onClick={() => handleCategoryChange(category.slug)}
            className={`rounded-full px-4 py-2 text-sm font-medium transition-colors ${
              selectedCategory === category.slug
                ? "bg-primary text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {category.name} ({category.count})
          </button>
        ))}
      </div>
    </div>
  );
}
