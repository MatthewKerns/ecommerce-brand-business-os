import { LoadingCard } from "@/components/LoadingCard";
import { SkeletonLoader } from "@/components/SkeletonLoader";

/**
 * Loading UI for System Health Page
 *
 * Automatically displayed by Next.js App Router when health page is loading.
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
          <SkeletonLoader variant="text" width="w-56" className="mb-2 h-8" />
          <SkeletonLoader variant="text" width="w-72" height="h-4" />
        </div>
      </div>

      {/* Overall Status Card Skeleton */}
      <LoadingCard variant="status" />

      {/* Section Header */}
      <SkeletonLoader variant="text" width="w-40" className="h-6" />

      {/* Service Status Cards Grid Skeleton */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <LoadingCard variant="status" />
        <LoadingCard variant="status" />
        <LoadingCard variant="status" />
        <LoadingCard variant="status" />
        <LoadingCard variant="status" />
        <LoadingCard variant="status" />
      </div>

      {/* Activity Log Skeleton */}
      <div className="mt-8">
        <SkeletonLoader variant="text" width="w-48" className="mb-4 h-6" />
        <LoadingCard variant="default" className="h-64" />
      </div>
    </div>
  );
}
