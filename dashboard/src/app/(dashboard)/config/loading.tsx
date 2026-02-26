import { LoadingCard } from "@/components/LoadingCard";
import { SkeletonLoader } from "@/components/SkeletonLoader";

/**
 * Loading UI for Configuration Page
 *
 * Automatically displayed by Next.js App Router when config page is loading.
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
          <SkeletonLoader variant="text" width="w-80" height="h-4" />
        </div>
      </div>

      {/* Tabs Skeleton */}
      <div className="flex gap-4 border-b border-slate-200">
        <SkeletonLoader variant="text" width="w-24" className="h-10" />
        <SkeletonLoader variant="text" width="w-24" className="h-10" />
        <SkeletonLoader variant="text" width="w-32" className="h-10" />
      </div>

      {/* Content Area Skeleton */}
      <div className="space-y-6">
        {/* Section Header */}
        <SkeletonLoader variant="text" width="w-40" className="h-6" />

        {/* Cards Grid */}
        <div className="grid gap-6 md:grid-cols-2">
          <LoadingCard variant="default" className="h-48" />
          <LoadingCard variant="default" className="h-48" />
          <LoadingCard variant="default" className="h-48" />
          <LoadingCard variant="default" className="h-48" />
        </div>
      </div>
    </div>
  );
}
