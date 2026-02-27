import { MetadataRoute } from 'next';
import { getAllPostsMeta, getAllCategories } from '@/lib/cms';

/**
 * Generate dynamic sitemap for the blog
 * Next.js 14 automatically generates sitemap.xml from this file
 * @see https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap
 */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://infinitycards.com';
  const blogPath = '/blog';

  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'yearly',
      priority: 1.0,
    },
    {
      url: `${baseUrl}${blogPath}`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.9,
    },
  ];

  // Blog post pages
  const posts = getAllPostsMeta();
  const postPages: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `${baseUrl}${blogPath}/${post.slug}`,
    lastModified: new Date(post.date),
    changeFrequency: 'weekly',
    priority: 0.8,
  }));

  // Category pages
  const categories = getAllCategories();
  const categoryPages: MetadataRoute.Sitemap = categories.map((category) => ({
    url: `${baseUrl}${blogPath}/category/${category.slug}`,
    lastModified: new Date(),
    changeFrequency: 'daily',
    priority: 0.7,
  }));

  return [...staticPages, ...postPages, ...categoryPages];
}
