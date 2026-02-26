"use client";

import { cn } from "@/lib/utils";

/**
 * SkeletonLoader component displays animated skeleton placeholders
 *
 * Features:
 * - Multiple variants: text, circle, rectangle, card
 * - Animated pulse effect
 * - Customizable width and height
 * - Composable for complex layouts
 * - Responsive design support
 *
 * @example
 * ```tsx
 * <SkeletonLoader variant="text" width="w-48" />
 * <SkeletonLoader variant="circle" className="h-12 w-12" />
 * <SkeletonLoader variant="rectangle" height="h-32" />
 * ```
 */

export interface SkeletonLoaderProps {
  /** Variant determines the skeleton shape and styling */
  variant?: "text" | "circle" | "rectangle" | "card";
  /** Width class (Tailwind utility) */
  width?: string;
  /** Height class (Tailwind utility) */
  height?: string;
  /** Number of repeated skeleton elements (useful for text lines) */
  count?: number;
  /** Optional custom className */
  className?: string;
}

export function SkeletonLoader({
  variant = "text",
  width,
  height,
  count = 1,
  className,
}: SkeletonLoaderProps) {
  // Base skeleton element
  const baseClasses = "animate-pulse bg-slate-200";

  // Variant-specific styling
  const variantClasses = {
    text: "h-4 rounded",
    circle: "rounded-full",
    rectangle: "rounded-md",
    card: "rounded-lg",
  };

  // Build skeleton element
  const skeletonElement = (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        width,
        height,
        className
      )}
    />
  );

  // Return multiple skeleton elements if count > 1
  if (count > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: count }).map((_, index) => (
          <div
            key={index}
            className={cn(
              baseClasses,
              variantClasses[variant],
              width,
              height,
              className
            )}
          />
        ))}
      </div>
    );
  }

  return skeletonElement;
}

/**
 * SkeletonText component - Convenient preset for text skeletons
 *
 * @example
 * ```tsx
 * <SkeletonText lines={3} />
 * ```
 */
export interface SkeletonTextProps {
  /** Number of text lines */
  lines?: number;
  /** Optional custom className */
  className?: string;
}

export function SkeletonText({ lines = 1, className }: SkeletonTextProps) {
  if (lines === 1) {
    return <SkeletonLoader variant="text" width="w-full" className={className} />;
  }

  return (
    <div className={cn("space-y-2", className)}>
      {Array.from({ length: lines }).map((_, index) => {
        // Make last line shorter for natural appearance
        const isLastLine = index === lines - 1;
        const width = isLastLine ? "w-2/3" : "w-full";

        return (
          <SkeletonLoader
            key={index}
            variant="text"
            width={width}
          />
        );
      })}
    </div>
  );
}

/**
 * SkeletonAvatar component - Convenient preset for circular avatars
 *
 * @example
 * ```tsx
 * <SkeletonAvatar size="md" />
 * ```
 */
export interface SkeletonAvatarProps {
  /** Size preset */
  size?: "sm" | "md" | "lg";
  /** Optional custom className */
  className?: string;
}

export function SkeletonAvatar({
  size = "md",
  className,
}: SkeletonAvatarProps) {
  const sizeClasses = {
    sm: "h-8 w-8",
    md: "h-12 w-12",
    lg: "h-16 w-16",
  };

  return (
    <SkeletonLoader
      variant="circle"
      className={cn(sizeClasses[size], className)}
    />
  );
}

/**
 * SkeletonCard component - Convenient preset for card skeletons
 *
 * @example
 * ```tsx
 * <SkeletonCard />
 * ```
 */
export interface SkeletonCardProps {
  /** Optional custom className */
  className?: string;
}

export function SkeletonCard({ className }: SkeletonCardProps) {
  return (
    <div className={cn("rounded-lg border border-slate-200 bg-white p-6", className)}>
      {/* Header */}
      <div className="mb-4 flex items-center gap-3">
        <SkeletonAvatar size="sm" />
        <div className="flex-1">
          <SkeletonLoader variant="text" width="w-32" className="mb-2" />
          <SkeletonLoader variant="text" width="w-20" height="h-3" />
        </div>
      </div>
      {/* Content */}
      <SkeletonText lines={3} />
    </div>
  );
}
