/**
 * TikTok Analytics Tests
 *
 * Test suite for TikTok Shop Client analytics functionality.
 */

import axios from 'axios';
import { TikTokShopClient } from '../tiktok-shop-client';
import type { TikTokShopConfig } from '../../types/config';
import type {
  TikTokVideoListResponse,
  TikTokAccountAnalytics,
  TikTokProductAnalytics,
} from '../../types/tiktok-analytics';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('TikTok analytics', () => {
  let client: TikTokShopClient;
  let mockHttpClient: {
    post: jest.Mock;
    get: jest.Mock;
    interceptors: {
      request: { use: jest.Mock };
    };
  };

  const config: TikTokShopConfig = {
    appKey: 'test-app-key',
    appSecret: 'test-app-secret',
    shopId: 'test-shop-id',
    accessToken: 'test-access-token',
    refreshToken: 'test-refresh-token',
    apiBaseUrl: 'https://api.tiktok.com',
  };

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Setup mock HTTP client
    mockHttpClient = {
      post: jest.fn(),
      get: jest.fn(),
      interceptors: {
        request: { use: jest.fn((interceptor) => interceptor) },
      },
    };

    mockedAxios.create = jest.fn().mockReturnValue(mockHttpClient);
    mockedAxios.isAxiosError = jest.fn().mockReturnValue(false);

    // Create client
    client = new TikTokShopClient(config);
  });

  describe('getVideoMetrics', () => {
    it('should fetch video metrics successfully', async () => {
      const mockResponse: TikTokVideoListResponse = {
        videos: [
          {
            video_id: 'video123',
            video_url: 'https://tiktok.com/@user/video/123',
            posted_at: 1700000000,
            views: 10000,
            likes: 500,
            comments: 50,
            shares: 25,
            saves: 100,
            shop_clicks: 200,
            product_views: 150,
            engagement_rate: 6.75,
            recorded_at: 1700100000,
          },
        ],
        total: 1,
        has_more: false,
      };

      mockHttpClient.post.mockResolvedValue({
        data: {
          code: 0,
          message: 'success',
          data: mockResponse,
          request_id: 'req123',
        },
      });

      const result = await client.getVideoMetrics({
        posted_from: 1700000000,
        posted_to: 1700200000,
        page_size: 10,
      });

      expect(result.videos).toHaveLength(1);
      expect(result.videos[0].video_id).toBe('video123');
      expect(result.videos[0].views).toBe(10000);
      expect(result.videos[0].shop_clicks).toBe(200);
      expect(mockHttpClient.post).toHaveBeenCalledWith(
        '/analytics/202309/videos/metrics',
        expect.objectContaining({
          shop_cipher: 'test-shop-id',
          posted_from: 1700000000,
          posted_to: 1700200000,
          page_size: 10,
        })
      );
    });

    it('should handle empty video list', async () => {
      const mockResponse: TikTokVideoListResponse = {
        videos: [],
        total: 0,
        has_more: false,
      };

      mockHttpClient.post.mockResolvedValue({
        data: {
          code: 0,
          message: 'success',
          data: mockResponse,
          request_id: 'req123',
        },
      });

      const result = await client.getVideoMetrics();

      expect(result.videos).toHaveLength(0);
      expect(result.total).toBe(0);
    });

    it('should add recorded_at timestamp if missing', async () => {
      const mockResponse: TikTokVideoListResponse = {
        videos: [
          {
            video_id: 'video456',
            posted_at: 1700000000,
            views: 5000,
            likes: 250,
            comments: 25,
            shares: 10,
            saves: 50,
          },
        ],
        total: 1,
        has_more: false,
      };

      mockHttpClient.post.mockResolvedValue({
        data: {
          code: 0,
          message: 'success',
          data: mockResponse,
          request_id: 'req123',
        },
      });

      const result = await client.getVideoMetrics();

      expect(result.videos[0].recorded_at).toBeDefined();
      expect(typeof result.videos[0].recorded_at).toBe('number');
    });

    it('should handle API errors', async () => {
      mockHttpClient.post.mockResolvedValue({
        data: {
          code: 1000001,
          message: 'Invalid parameters',
          data: null,
          request_id: 'req123',
        },
      });

      await expect(client.getVideoMetrics()).rejects.toThrow(
        'Get video metrics failed: Invalid parameters'
      );
    });
  });

  describe('getAccountAnalytics', () => {
    it('should fetch account analytics successfully', async () => {
      const mockResponse: TikTokAccountAnalytics = {
        account_id: 'account123',
        date_range_start: 1700000000,
        date_range_end: 1700200000,
        total_followers: 10000,
        follower_growth: 500,
        total_videos: 50,
        total_views: 500000,
        total_likes: 25000,
        total_comments: 2500,
        total_shares: 1250,
        total_saves: 5000,
        total_shop_clicks: 10000,
        total_product_views: 8000,
        avg_engagement_rate: 6.5,
        avg_completion_rate: 45.0,
        recorded_at: 1700200000,
      };

      mockHttpClient.post.mockResolvedValue({
        data: {
          code: 0,
          message: 'success',
          data: mockResponse,
          request_id: 'req123',
        },
      });

      const result = await client.getAccountAnalytics({
        date_from: 1700000000,
        date_to: 1700200000,
      });

      expect(result.account_id).toBe('account123');
      expect(result.total_views).toBe(500000);
      expect(result.total_shop_clicks).toBe(10000);
      expect(result.follower_growth).toBe(500);
      expect(mockHttpClient.post).toHaveBeenCalledWith(
        '/analytics/202309/account/summary',
        expect.objectContaining({
          shop_cipher: 'test-shop-id',
          date_from: 1700000000,
          date_to: 1700200000,
        })
      );
    });

    it('should add recorded_at timestamp if missing', async () => {
      const mockResponse = {
        account_id: 'account123',
        date_range_start: 1700000000,
        date_range_end: 1700200000,
        total_followers: 10000,
        follower_growth: 500,
        total_videos: 50,
        total_views: 500000,
        total_likes: 25000,
        total_comments: 2500,
        total_shares: 1250,
        total_saves: 5000,
      };

      mockHttpClient.post.mockResolvedValue({
        data: {
          code: 0,
          message: 'success',
          data: mockResponse,
          request_id: 'req123',
        },
      });

      const result = await client.getAccountAnalytics({
        date_from: 1700000000,
        date_to: 1700200000,
      });

      expect(result.recorded_at).toBeDefined();
      expect(typeof result.recorded_at).toBe('number');
    });
  });

  describe('getProductAnalytics', () => {
    it('should fetch product analytics successfully', async () => {
      const mockProducts: TikTokProductAnalytics[] = [
        {
          product_id: 'prod123',
          product_name: 'Test Product',
          date_range_start: 1700000000,
          date_range_end: 1700200000,
          product_views: 5000,
          product_clicks: 1000,
          add_to_cart: 200,
          purchases: 50,
          gross_sales: 2500.0,
          units_sold: 50,
          conversion_rate: 5.0,
          recorded_at: 1700200000,
        },
      ];

      mockHttpClient.post.mockResolvedValue({
        data: {
          code: 0,
          message: 'success',
          data: { products: mockProducts },
          request_id: 'req123',
        },
      });

      const result = await client.getProductAnalytics({
        date_from: 1700000000,
        date_to: 1700200000,
        product_ids: ['prod123'],
      });

      expect(result).toHaveLength(1);
      expect(result[0].product_id).toBe('prod123');
      expect(result[0].product_views).toBe(5000);
      expect(result[0].purchases).toBe(50);
      expect(result[0].gross_sales).toBe(2500.0);
      expect(mockHttpClient.post).toHaveBeenCalledWith(
        '/analytics/202309/products/metrics',
        expect.objectContaining({
          shop_cipher: 'test-shop-id',
          date_from: 1700000000,
          date_to: 1700200000,
          product_ids: ['prod123'],
        })
      );
    });

    it('should handle multiple products', async () => {
      const mockProducts: TikTokProductAnalytics[] = [
        {
          product_id: 'prod1',
          product_name: 'Product 1',
          date_range_start: 1700000000,
          date_range_end: 1700200000,
          product_views: 3000,
          product_clicks: 600,
          recorded_at: 1700200000,
        },
        {
          product_id: 'prod2',
          product_name: 'Product 2',
          date_range_start: 1700000000,
          date_range_end: 1700200000,
          product_views: 2000,
          product_clicks: 400,
          recorded_at: 1700200000,
        },
      ];

      mockHttpClient.post.mockResolvedValue({
        data: {
          code: 0,
          message: 'success',
          data: { products: mockProducts },
          request_id: 'req123',
        },
      });

      const result = await client.getProductAnalytics({
        date_from: 1700000000,
        date_to: 1700200000,
      });

      expect(result).toHaveLength(2);
      expect(result[0].product_id).toBe('prod1');
      expect(result[1].product_id).toBe('prod2');
    });

    it('should add recorded_at timestamp if missing', async () => {
      const mockProducts = [
        {
          product_id: 'prod123',
          product_name: 'Test Product',
          date_range_start: 1700000000,
          date_range_end: 1700200000,
          product_views: 5000,
          product_clicks: 1000,
        },
      ];

      mockHttpClient.post.mockResolvedValue({
        data: {
          code: 0,
          message: 'success',
          data: { products: mockProducts },
          request_id: 'req123',
        },
      });

      const result = await client.getProductAnalytics({
        date_from: 1700000000,
        date_to: 1700200000,
      });

      expect(result[0].recorded_at).toBeDefined();
      expect(typeof result[0].recorded_at).toBe('number');
    });
  });

  describe('Analytics error handling', () => {
    it('should handle rate limit errors for video metrics', async () => {
      mockHttpClient.post.mockResolvedValue({
        data: {
          code: 1000002,
          message: 'Rate limit exceeded',
          data: null,
          request_id: 'req123',
        },
      });

      await expect(client.getVideoMetrics()).rejects.toThrow(
        'Get video metrics failed: Rate limit exceeded'
      );
    });

    it('should handle network errors', async () => {
      mockedAxios.isAxiosError = jest.fn().mockReturnValue(true);
      const networkError = new Error('Network error');
      mockHttpClient.post.mockRejectedValue(networkError);

      await expect(client.getVideoMetrics()).rejects.toBeDefined();
    });
  });

  describe('Analytics data validation', () => {
    it('should validate video metrics schema', async () => {
      const invalidResponse = {
        videos: [
          {
            video_id: 'video123',
            posted_at: 'invalid-timestamp', // Should be number
            views: -100, // Should be non-negative
          },
        ],
        total: 1,
        has_more: false,
      };

      mockHttpClient.post.mockResolvedValue({
        data: {
          code: 0,
          message: 'success',
          data: invalidResponse,
          request_id: 'req123',
        },
      });

      await expect(client.getVideoMetrics()).rejects.toThrow();
    });

    it('should validate account analytics schema', async () => {
      const invalidResponse = {
        account_id: 'account123',
        date_range_start: 1700000000,
        date_range_end: 1700200000,
        total_followers: -100, // Should be non-negative
      };

      mockHttpClient.post.mockResolvedValue({
        data: {
          code: 0,
          message: 'success',
          data: invalidResponse,
          request_id: 'req123',
        },
      });

      await expect(
        client.getAccountAnalytics({
          date_from: 1700000000,
          date_to: 1700200000,
        })
      ).rejects.toThrow();
    });
  });
});
