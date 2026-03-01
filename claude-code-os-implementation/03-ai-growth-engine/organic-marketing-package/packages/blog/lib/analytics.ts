/**
 * Google Analytics 4 (GA4) Tracking Utilities
 *
 * Provides functions for tracking pageviews and custom events in GA4.
 * Requires NEXT_PUBLIC_GA_MEASUREMENT_ID environment variable.
 */

// Type definitions for gtag
declare global {
  interface Window {
    gtag?: (
      command: string,
      targetId: string,
      config?: Record<string, any>
    ) => void;
    dataLayer?: any[];
  }
}

/**
 * Get the GA Measurement ID from environment variables
 */
export const GA_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID;

/**
 * Check if GA4 tracking is enabled
 * GA4 is enabled when:
 * 1. Measurement ID is provided
 * 2. Not in development mode (optional check)
 */
export const isGAEnabled = (): boolean => {
  return !!GA_MEASUREMENT_ID && GA_MEASUREMENT_ID !== 'G-XXXXXXXXXX';
};

/**
 * Track a pageview in Google Analytics
 * @param url - The page URL to track
 */
export const pageview = (url: string): void => {
  if (!isGAEnabled() || typeof window === 'undefined') {
    return;
  }

  window.gtag?.('config', GA_MEASUREMENT_ID as string, {
    page_path: url,
  });
};

/**
 * Track a custom event in Google Analytics
 * @param action - The event action (e.g., 'click', 'share')
 * @param params - Additional event parameters
 */
export const event = (
  action: string,
  params?: Record<string, any>
): void => {
  if (!isGAEnabled() || typeof window === 'undefined') {
    return;
  }

  window.gtag?.('event', action, params);
};

/**
 * Track blog post read events
 * @param postSlug - The blog post slug
 * @param postTitle - The blog post title
 * @param category - The blog post category
 */
export const trackBlogPostView = (
  postSlug: string,
  postTitle: string,
  category: string
): void => {
  event('view_blog_post', {
    post_slug: postSlug,
    post_title: postTitle,
    post_category: category,
  });
};

/**
 * Track social share events
 * @param platform - The social platform (e.g., 'twitter', 'facebook')
 * @param url - The URL being shared
 */
export const trackSocialShare = (platform: string, url: string): void => {
  event('share', {
    method: platform,
    content_type: 'blog_post',
    item_id: url,
  });
};

/**
 * Track category filter usage
 * @param category - The selected category
 */
export const trackCategoryFilter = (category: string): void => {
  event('filter_category', {
    category: category,
  });
};

/**
 * Track search events
 * @param searchTerm - The search term entered
 */
export const trackSearch = (searchTerm: string): void => {
  event('search', {
    search_term: searchTerm,
  });
};

/**
 * Track outbound link clicks
 * @param url - The external URL clicked
 */
export const trackOutboundLink = (url: string): void => {
  event('click', {
    event_category: 'outbound',
    event_label: url,
    transport_type: 'beacon',
  });
};

/**
 * Track time spent on page (call when user leaves)
 * @param timeInSeconds - Time spent in seconds
 * @param pageTitle - The page title
 */
export const trackTimeOnPage = (
  timeInSeconds: number,
  pageTitle: string
): void => {
  event('engagement_time', {
    page_title: pageTitle,
    time_seconds: timeInSeconds,
  });
};
