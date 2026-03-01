import Link from "next/link";
import type { BlogPostMeta } from "@/lib/types";

interface BlogCardProps {
  post: BlogPostMeta;
}

export function BlogCard({ post }: BlogCardProps) {
  const formattedDate = new Date(post.date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <article className="group relative flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-all hover:shadow-md">
      {post.image && (
        <div className="aspect-video w-full overflow-hidden bg-gray-100">
          <img
            src={post.image}
            alt={post.title}
            className="h-full w-full object-cover transition-transform group-hover:scale-105"
          />
        </div>
      )}
      <div className="flex flex-1 flex-col p-6">
        <div className="mb-3 flex items-center gap-3 text-sm text-gray-500">
          <time dateTime={post.date}>{formattedDate}</time>
          <span className="text-gray-300">•</span>
          <span>{post.readingTime} min read</span>
        </div>

        <Link href={`/blog/${post.slug}`} className="group-hover:text-primary">
          <h2 className="mb-2 text-2xl font-bold text-gray-900 transition-colors">
            {post.title}
          </h2>
        </Link>

        <p className="mb-4 flex-1 text-gray-600 line-clamp-3">
          {post.description}
        </p>

        <div className="flex flex-wrap items-center gap-2">
          <Link
            href={`/blog/category/${post.category}`}
            className="rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary transition-colors hover:bg-primary/20"
          >
            {post.category
              .split("-")
              .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
              .join(" ")}
          </Link>

          {post.tags.slice(0, 2).map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600"
            >
              {tag}
            </span>
          ))}
        </div>

        <div className="mt-4 flex items-center justify-between border-t border-gray-100 pt-4">
          <span className="text-sm text-gray-500">{post.author}</span>
          <Link
            href={`/blog/${post.slug}`}
            className="text-sm font-medium text-primary hover:underline"
          >
            Read more →
          </Link>
        </div>
      </div>
    </article>
  );
}
