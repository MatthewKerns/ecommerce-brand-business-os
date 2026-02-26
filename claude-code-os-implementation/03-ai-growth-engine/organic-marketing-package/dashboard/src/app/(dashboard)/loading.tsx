import { LoadingCard } from "@/components/LoadingCard";
import { SkeletonLoader, SkeletonText } from "@/components/SkeletonLoader";

/**
 * Loading UI for Dashboard Routes
 *
 * Automatically displayed by Next.js App Router when route is loading.
 * Uses Suspense boundary to show skeleton screens during data fetching.
 *
 * @see https://nextjs.org/docs/app/api-reference/file-conventions/loading
 */
export default function Loading() {
  return (
    <div className="space-y-6">
      {/* Page Header Skeleton */}
      <div className="flex items-center gap-3">
        <SkeletonLoader variant="rectangle" className="h-12 w-12" />
        <div className="flex-1">
          <SkeletonLoader variant="text" width="w-48" className="mb-2 h-8" />
          <SkeletonLoader variant="text" width="w-64" height="h-4" />
        </div>
      </div>

      {/* Section Header Skeleton */}
      <div>
        <SkeletonLoader variant="text" width="w-56" className="mb-4 h-6" />
      </div>

      {/* KPI Cards Grid Skeleton */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <LoadingCard variant="metric" />
        <LoadingCard variant="metric" />
        <LoadingCard variant="metric" />
        <LoadingCard variant="metric" />
        <LoadingCard variant="metric" />
        <LoadingCard variant="metric" />
      </div>

      {/* Additional Content Skeleton */}
      <div className="mt-8">
        <SkeletonLoader variant="text" width="w-48" className="mb-4 h-6" />
        <div className="grid gap-6 md:grid-cols-2">
          <LoadingCard variant="default" />
          <LoadingCard variant="default" />
        </div>
      </div>
    </div>
  );
}
