import Link from 'next/link';
import type { BlogPost } from '@/lib/types';

interface RelatedPostsProps {
  posts: BlogPost[];
}

export function RelatedPosts({ posts }: RelatedPostsProps) {
  if (posts.length === 0) {
    return null;
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="mb-6 text-xl font-bold text-gray-900">Related Articles</h3>
      <div className="space-y-4">
        {posts.map((post) => {
          const formattedDate = new Date(post.date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
          });

          return (
            <article key={post.slug} className="group">
              <Link
                href={`/blog/${post.slug}`}
                className="block space-y-2 transition-all hover:translate-x-1"
              >
                {post.image && (
                  <div className="aspect-video w-full overflow-hidden rounded-md bg-gray-100">
                    <img
                      src={post.image}
                      alt={post.title}
                      className="h-full w-full object-cover transition-transform group-hover:scale-105"
                    />
                  </div>
                )}
                <div>
                  <h4 className="font-semibold text-gray-900 group-hover:text-primary">
                    {post.title}
                  </h4>
                  <p className="mt-1 text-sm text-gray-600 line-clamp-2">
                    {post.description}
                  </p>
                  <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
                    <time dateTime={post.date}>{formattedDate}</time>
                    <span>•</span>
                    <span>{post.readingTime} min read</span>
                  </div>
                </div>
              </Link>
            </article>
          );
        })}
      </div>
    </div>
  );
}
