import { LoadingCard } from "@/components/LoadingCard";
import { SkeletonLoader } from "@/components/SkeletonLoader";

/**
 * Loading UI for Analytics Page
 *
 * Automatically displayed by Next.js App Router when analytics page is loading.
 *
 * @see https://nextjs.org/docs/app/api-reference/file-conventions/loading
 */
export default function Loading() {
  return (
    <div className="space-y-6">
      {/* Page Header Skeleton */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <SkeletonLoader variant="rectangle" className="h-12 w-12" />
          <div className="flex-1">
            <SkeletonLoader variant="text" width="w-48" className="mb-2 h-8" />
            <SkeletonLoader variant="text" width="w-64" height="h-4" />
          </div>
        </div>
        {/* Date Range Selector Skeleton */}
        <SkeletonLoader variant="rectangle" width="w-48" className="h-10" />
      </div>

      {/* Key Metrics Grid Skeleton */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <LoadingCard variant="metric" />
        <LoadingCard variant="metric" />
        <LoadingCard variant="metric" />
        <LoadingCard variant="metric" />
      </div>

      {/* Performance Chart Skeleton */}
      <div>
        <SkeletonLoader variant="text" width="w-48" className="mb-4 h-6" />
        <LoadingCard variant="default" className="h-80" />
      </div>

      {/* Channel Breakdown Skeleton */}
      <div>
        <SkeletonLoader variant="text" width="w-56" className="mb-4 h-6" />
        <div className="grid gap-6 md:grid-cols-3">
          <LoadingCard variant="default" className="h-48" />
          <LoadingCard variant="default" className="h-48" />
          <LoadingCard variant="default" className="h-48" />
        </div>
      </div>
    </div>
  );
}
