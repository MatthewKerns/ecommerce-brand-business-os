import { MDXRemote } from 'next-mdx-remote/rsc';
import { Calendar, Clock, User } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import type { BlogPost as BlogPostType } from '@/lib/types';
import rehypeHighlight from 'rehype-highlight';
import rehypeSlug from 'rehype-slug';
import remarkGfm from 'remark-gfm';

interface BlogPostProps {
  post: BlogPostType;
}

// Custom components for MDX
const components = {
  h1: (props: any) => (
    <h1
      id={props.children?.toString().toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-')}
      className="mb-6 mt-8 text-4xl font-bold text-gray-900"
      {...props}
    />
  ),
  h2: (props: any) => (
    <h2
      id={props.children?.toString().toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-')}
      className="mb-4 mt-8 text-3xl font-bold text-gray-900"
      {...props}
    />
  ),
  h3: (props: any) => (
    <h3
      id={props.children?.toString().toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-')}
      className="mb-3 mt-6 text-2xl font-semibold text-gray-900"
      {...props}
    />
  ),
  h4: (props: any) => (
    <h4
      className="mb-2 mt-4 text-xl font-semibold text-gray-900"
      {...props}
    />
  ),
  p: (props: any) => (
    <p className="mb-4 leading-7 text-gray-700" {...props} />
  ),
  a: (props: any) => (
    <a
      className="font-medium text-primary underline decoration-primary/30 underline-offset-2 transition-colors hover:decoration-primary"
      {...props}
    />
  ),
  ul: (props: any) => (
    <ul className="mb-4 ml-6 list-disc space-y-2 text-gray-700" {...props} />
  ),
  ol: (props: any) => (
    <ol className="mb-4 ml-6 list-decimal space-y-2 text-gray-700" {...props} />
  ),
  li: (props: any) => (
    <li className="leading-7" {...props} />
  ),
  blockquote: (props: any) => (
    <blockquote
      className="my-6 border-l-4 border-primary/50 bg-gray-50 py-3 pl-6 pr-4 italic text-gray-700"
      {...props}
    />
  ),
  code: (props: any) => (
    <code
      className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-sm text-gray-800"
      {...props}
    />
  ),
  pre: (props: any) => (
    <pre
      className="mb-4 overflow-x-auto rounded-lg bg-gray-900 p-4 text-sm text-gray-100"
      {...props}
    />
  ),
  img: (props: any) => (
    <img
      className="my-6 rounded-lg shadow-md"
      loading="lazy"
      {...props}
    />
  ),
  hr: (props: any) => (
    <hr className="my-8 border-gray-200" {...props} />
  ),
  table: (props: any) => (
    <div className="my-6 overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200" {...props} />
    </div>
  ),
  th: (props: any) => (
    <th className="bg-gray-50 px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700" {...props} />
  ),
  td: (props: any) => (
    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-700" {...props} />
  ),
};

export async function BlogPost({ post }: BlogPostProps) {
  const formattedDate = new Date(post.date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <article className="mx-auto max-w-4xl">
      {/* Header */}
      <header className="mb-8">
        {/* Breadcrumb */}
        <nav className="mb-6 flex items-center gap-2 text-sm text-gray-600">
          <Link href="/blog" className="hover:text-primary">
            Blog
          </Link>
          <span>/</span>
          <Link
            href={`/blog/category/${post.category}`}
            className="hover:text-primary"
          >
            {post.category
              .split('-')
              .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
              .join(' ')}
          </Link>
        </nav>

        {/* Title */}
        <h1 className="mb-4 text-4xl font-bold text-gray-900 md:text-5xl">
          {post.title}
        </h1>

        {/* Description */}
        <p className="mb-6 text-xl text-gray-600">{post.description}</p>

        {/* Meta */}
        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <User className="h-4 w-4" />
            <span>{post.author}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <time dateTime={post.date}>{formattedDate}</time>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            <span>{post.readingTime} min read</span>
          </div>
        </div>

        {/* Tags */}
        {post.tags.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {post.tags.map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-gray-100 px-3 py-1 text-sm font-medium text-gray-600"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </header>

      {/* Featured Image */}
      {post.image && (
        <div className="relative mb-8 aspect-video w-full overflow-hidden rounded-lg bg-gray-100">
          <Image
            src={post.image}
            alt={post.title}
            fill
            priority
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
            className="object-cover"
          />
        </div>
      )}

      {/* Content */}
      <div className="prose prose-lg max-w-none prose-headings:font-bold prose-a:text-primary">
        <MDXRemote
          source={post.content}
          components={components}
          options={{
            mdxOptions: {
              remarkPlugins: [remarkGfm],
              rehypePlugins: [rehypeSlug, rehypeHighlight],
            },
          }}
        />
      </div>
    </article>
  );
}
