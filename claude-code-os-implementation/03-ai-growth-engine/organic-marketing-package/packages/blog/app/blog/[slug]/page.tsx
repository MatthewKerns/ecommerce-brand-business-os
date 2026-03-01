import { notFound } from 'next/navigation';
import { getPostBySlug, getAllPosts, getRelatedPosts } from '@/lib/cms';
import { generatePostMetadata } from '@/lib/seo';
import {
  generateArticleSchema,
  generateBreadcrumbSchema,
} from '@/lib/structuredData';
import { BlogPost } from '@/components/BlogPost';
import { TableOfContents } from '@/components/TableOfContents';
import { ShareButtons } from '@/components/ShareButtons';
import { RelatedPosts } from '@/components/RelatedPosts';
import type { Metadata } from 'next';

interface BlogPostPageProps {
  params: {
    slug: string;
  };
}

// Generate static paths for all blog posts
export async function generateStaticParams() {
  const posts = getAllPosts();
  return posts.map((post) => ({
    slug: post.slug,
  }));
}

// Generate metadata for SEO
export async function generateMetadata({
  params,
}: BlogPostPageProps): Promise<Metadata> {
  const post = getPostBySlug(params.slug);

  if (!post) {
    return {
      title: 'Post Not Found',
      robots: {
        index: false,
        follow: false,
      },
    };
  }

  // Use SEO utility to generate comprehensive metadata
  return generatePostMetadata(post);
}

export default function BlogPostPage({ params }: BlogPostPageProps) {
  const post = getPostBySlug(params.slug);

  if (!post || !post.published) {
    notFound();
  }

  const relatedPosts = getRelatedPosts(params.slug, 3);

  // Generate structured data for SEO (Schema.org JSON-LD)
  const articleStructuredData = generateArticleSchema(post);
  const breadcrumbStructuredData = generateBreadcrumbSchema(post);

  return (
    <>
      {/* JSON-LD Structured Data - Article Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(articleStructuredData),
        }}
      />
      {/* JSON-LD Structured Data - Breadcrumb Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(breadcrumbStructuredData),
        }}
      />

      <div className="container mx-auto px-4 py-12">
        <div className="flex flex-col gap-8 lg:flex-row">
          {/* Main Content */}
          <div className="flex-1">
            <BlogPost post={post} />

            {/* Share Buttons - Mobile */}
            <div className="mt-12 lg:hidden">
              <ShareButtons
                title={post.title}
                description={post.description}
                slug={post.slug}
              />
            </div>

            {/* Related Posts - Mobile */}
            {relatedPosts.length > 0 && (
              <div className="mt-8 lg:hidden">
                <RelatedPosts posts={relatedPosts} />
              </div>
            )}
          </div>

          {/* Sidebar - Desktop */}
          <aside className="hidden w-80 shrink-0 space-y-8 lg:block">
            {/* Table of Contents */}
            <TableOfContents content={post.content} />

            {/* Share Buttons */}
            <ShareButtons
              title={post.title}
              description={post.description}
              slug={post.slug}
            />

            {/* Related Posts */}
            {relatedPosts.length > 0 && <RelatedPosts posts={relatedPosts} />}
          </aside>
        </div>
      </div>
    </>
  );
}
