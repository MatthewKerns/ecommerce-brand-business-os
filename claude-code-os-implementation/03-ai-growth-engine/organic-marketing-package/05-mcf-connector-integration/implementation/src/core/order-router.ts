/**
 * Order Router - Orchestrates the full TikTok-to-MCF order routing flow
 *
 * Features:
 * - Fetches orders from TikTok Shop
 * - Validates orders for MCF fulfillment
 * - Checks inventory availability
 * - Transforms orders to MCF format
 * - Creates fulfillment orders in Amazon MCF
 * - Tracks routing results and errors
 */

import type { TikTokShopClient } from '../clients/tiktok-shop-client';
import type { AmazonMCFClient } from '../clients/amazon-mcf-client';
import type { OrderValidator } from './order-validator';
import type { OrderTransformer } from './order-transformer';
import type { InventorySync } from './inventory-sync';
import type { TikTokOrder } from '../types/tiktok-order';
import type { MCFFulfillmentOrder } from '../types/mcf-order';
import { ErrorCode, TikTokOrderStatus } from '../types/common';

// ============================================================
// Types
// ============================================================

export interface OrderRoutingError {
  orderId: string;
  stage: 'fetch' | 'validate' | 'transform' | 'check_inventory' | 'create_mcf';
  code: ErrorCode;
  message: string;
  details?: unknown;
}

export interface OrderRoutingWarning {
  orderId: string;
  stage: 'validate' | 'transform' | 'check_inventory';
  message: string;
}

export interface OrderRoutingSuccess {
  orderId: string;
  tiktokOrder: TikTokOrder;
  mcfFulfillmentOrderId: string;
  mcfOrder?: MCFFulfillmentOrder;
  warnings?: OrderRoutingWarning[];
}

export interface OrderRoutingResult {
  success: boolean;
  orderId: string;
  successResult?: OrderRoutingSuccess;
  error?: OrderRoutingError;
}

export interface BatchRoutingResult {
  totalOrders: number;
  successCount: number;
  failureCount: number;
  results: OrderRoutingResult[];
  errors: OrderRoutingError[];
}

export interface OrderRouterConfig {
  continueOnError?: boolean;
  maxConcurrentOrders?: number;
}

export interface OrderRouterDependencies {
  tiktokClient: TikTokShopClient;
  amazonClient: AmazonMCFClient;
  validator: OrderValidator;
  transformer: OrderTransformer;
  inventorySync?: InventorySync; // Optional - if not provided, inventory checks are skipped
}

// ============================================================
// Constants
// ============================================================

const DEFAULT_ROUTER_CONFIG: Required<OrderRouterConfig> = {
  continueOnError: true,
  maxConcurrentOrders: 5,
};

// ============================================================
// OrderRouter Class
// ============================================================

/**
 * OrderRouter orchestrates the full order routing flow from TikTok to Amazon MCF
 */
export class OrderRouter {
  private config: Required<OrderRouterConfig>;
  private tiktokClient: TikTokShopClient;
  private amazonClient: AmazonMCFClient;
  private validator: OrderValidator;
  private transformer: OrderTransformer;
  private inventorySync?: InventorySync;

  constructor(
    dependencies: OrderRouterDependencies,
    config?: OrderRouterConfig
  ) {
    this.tiktokClient = dependencies.tiktokClient;
    this.amazonClient = dependencies.amazonClient;
    this.validator = dependencies.validator;
    this.transformer = dependencies.transformer;
    this.inventorySync = dependencies.inventorySync;
    this.config = { ...DEFAULT_ROUTER_CONFIG, ...config };
  }

  /**
   * Route a single TikTok order to Amazon MCF
   */
  async routeOrder(orderId: string): Promise<OrderRoutingResult> {
    try {
      // Stage 1: Fetch order from TikTok
      let tiktokOrder: TikTokOrder;
      try {
        tiktokOrder = await this.tiktokClient.getOrderDetail(orderId);
      } catch (error) {
        return {
          success: false,
          orderId,
          error: {
            orderId,
            stage: 'fetch',
            code: ErrorCode.TIKTOK_API_ERROR,
            message: `Failed to fetch order from TikTok: ${error instanceof Error ? error.message : 'Unknown error'}`,
            details: error,
          },
        };
      }

      // Stage 2: Validate order
      const validationResult = this.validator.validateOrder(tiktokOrder);
      if (!validationResult.valid) {
        return {
          success: false,
          orderId,
          error: {
            orderId,
            stage: 'validate',
            code: ErrorCode.INVALID_ORDER_DATA,
            message: `Order validation failed: ${validationResult.errors.map(e => e.message).join(', ')}`,
            details: validationResult.errors,
          },
        };
      }

      // Collect validation warnings
      const warnings: OrderRoutingWarning[] = [];
      if (validationResult.warnings) {
        warnings.push(
          ...validationResult.warnings.map(w => ({
            orderId,
            stage: 'validate' as const,
            message: w.message,
          }))
        );
      }

      // Stage 3: Transform order
      const transformResult = this.transformer.transformOrder(
        validationResult.normalizedOrder!,
        validationResult.normalizedAddress!
      );

      if (!transformResult.success) {
        return {
          success: false,
          orderId,
          error: {
            orderId,
            stage: 'transform',
            code: ErrorCode.TRANSFORMATION_FAILED,
            message: `Order transformation failed: ${transformResult.errors.map(e => e.message).join(', ')}`,
            details: transformResult.errors,
          },
        };
      }

      // Collect transformation warnings
      if (transformResult.warnings) {
        warnings.push(
          ...transformResult.warnings.map(w => ({
            orderId,
            stage: 'transform' as const,
            message: w.message,
          }))
        );
      }

      // Stage 3.5: Check inventory (if inventory sync is enabled)
      if (this.inventorySync && transformResult.mcfOrderRequest) {
        try {
          // Extract SKUs and quantities from MCF order request
          const skuQuantities = transformResult.mcfOrderRequest.items.map(item => ({
            sku: item.sellerSku,
            quantity: item.quantity,
          }));

          // Check inventory for all SKUs
          const inventoryResult = await this.inventorySync.checkInventoryBatch(skuQuantities);

          // Check for insufficient inventory
          const insufficientItems = inventoryResult.results.filter(r => !r.sufficient);
          if (insufficientItems.length > 0) {
            const insufficientSkus = insufficientItems.map(item =>
              `${item.sku} (requested: ${item.requested}, available: ${item.available})`
            ).join(', ');

            return {
              success: false,
              orderId,
              error: {
                orderId,
                stage: 'check_inventory',
                code: ErrorCode.INSUFFICIENT_INVENTORY,
                message: `Insufficient inventory for order: ${insufficientSkus}`,
                details: {
                  insufficientItems: insufficientItems.map(item => ({
                    sku: item.sku,
                    requested: item.requested,
                    available: item.available,
                    error: item.error,
                  })),
                  inventoryResult,
                },
              },
            };
          }

          // Collect low stock warnings
          const lowStockItems = inventoryResult.results.filter(r => r.lowStock && r.sufficient);
          if (lowStockItems.length > 0) {
            warnings.push(
              ...lowStockItems.map(item => ({
                orderId,
                stage: 'check_inventory' as const,
                message: `Low stock for SKU ${item.sku}: ${item.available} available (threshold: ${this.inventorySync!.getConfig().lowStockThreshold})`,
              }))
            );
          }

          // Collect inventory check errors (non-blocking)
          if (inventoryResult.errorCount > 0) {
            warnings.push(
              ...inventoryResult.errors.map(error => ({
                orderId,
                stage: 'check_inventory' as const,
                message: `Inventory check warning for SKU ${error.sku}: ${error.message}`,
              }))
            );
          }
        } catch (error) {
          // Inventory check failure - treat as blocking error
          return {
            success: false,
            orderId,
            error: {
              orderId,
              stage: 'check_inventory',
              code: ErrorCode.INVENTORY_CHECK_FAILED,
              message: `Failed to check inventory: ${error instanceof Error ? error.message : 'Unknown error'}`,
              details: error,
            },
          };
        }
      }

      // Stage 4: Create MCF fulfillment order
      let mcfOrder: MCFFulfillmentOrder | undefined;
      let mcfFulfillmentOrderId: string;

      try {
        const mcfRequest = transformResult.mcfOrderRequest!;

        // Convert MCFFulfillmentOrderRequest to CreateMCFOrderParams
        const createParams = {
          orderId: mcfRequest.sellerFulfillmentOrderId,
          displayableOrderId: mcfRequest.displayableOrderId,
          orderDate: new Date(mcfRequest.displayableOrderDate),
          orderComment: mcfRequest.displayableOrderComment,
          shippingSpeed: mcfRequest.shippingSpeedCategory,
          destinationAddress: mcfRequest.destinationAddress,
          items: mcfRequest.items.map(item => ({
            sku: item.sellerSku,
            itemId: item.sellerFulfillmentOrderItemId,
            quantity: item.quantity,
            price: item.perUnitPrice
              ? { amount: item.perUnitPrice.value, currency: item.perUnitPrice.currencyCode }
              : undefined,
            declaredValue: item.perUnitDeclaredValue
              ? { amount: item.perUnitDeclaredValue.value, currency: item.perUnitDeclaredValue.currencyCode }
              : undefined,
          })),
        };

        const createResult = await this.amazonClient.createFulfillmentOrder(createParams);
        mcfFulfillmentOrderId = mcfRequest.sellerFulfillmentOrderId;

        // Try to get the created order details (optional - don't fail if this fails)
        try {
          const orderDetail = await this.amazonClient.getFulfillmentOrder({
            sellerFulfillmentOrderId: mcfFulfillmentOrderId,
          });
          mcfOrder = orderDetail.fulfillmentOrder;
        } catch (detailError) {
          // Ignore error - order was created successfully, we just couldn't fetch details
        }
      } catch (error) {
        return {
          success: false,
          orderId,
          error: {
            orderId,
            stage: 'create_mcf',
            code: ErrorCode.AMAZON_API_ERROR,
            message: `Failed to create MCF fulfillment order: ${error instanceof Error ? error.message : 'Unknown error'}`,
            details: error,
          },
        };
      }

      // Success!
      return {
        success: true,
        orderId,
        successResult: {
          orderId,
          tiktokOrder,
          mcfFulfillmentOrderId,
          mcfOrder,
          warnings: warnings.length > 0 ? warnings : undefined,
        },
      };
    } catch (error) {
      // Unexpected error
      return {
        success: false,
        orderId,
        error: {
          orderId,
          stage: 'fetch',
          code: ErrorCode.UNKNOWN_ERROR,
          message: `Unexpected error routing order: ${error instanceof Error ? error.message : 'Unknown error'}`,
          details: error,
        },
      };
    }
  }

  /**
   * Route multiple TikTok orders to Amazon MCF
   */
  async routeOrders(orderIds: string[]): Promise<BatchRoutingResult> {
    const results: OrderRoutingResult[] = [];
    const errors: OrderRoutingError[] = [];

    // Process orders in batches to respect max concurrent limit
    for (let i = 0; i < orderIds.length; i += this.config.maxConcurrentOrders) {
      const batch = orderIds.slice(i, i + this.config.maxConcurrentOrders);

      // Process batch concurrently
      const batchResults = await Promise.all(
        batch.map(orderId => this.routeOrder(orderId))
      );

      results.push(...batchResults);

      // Collect errors
      for (const result of batchResults) {
        if (!result.success && result.error) {
          errors.push(result.error);

          // If not continuing on error, stop processing
          if (!this.config.continueOnError) {
            break;
          }
        }
      }

      // If not continuing on error and we have errors, stop
      if (!this.config.continueOnError && errors.length > 0) {
        break;
      }
    }

    const successCount = results.filter(r => r.success).length;
    const failureCount = results.filter(r => !r.success).length;

    return {
      totalOrders: orderIds.length,
      successCount,
      failureCount,
      results,
      errors,
    };
  }

  /**
   * Route all pending TikTok orders to Amazon MCF
   *
   * Fetches all orders with AWAITING_SHIPMENT or AWAITING_COLLECTION status
   * and routes them to MCF.
   */
  async routePendingOrders(): Promise<BatchRoutingResult> {
    try {
      // Fetch all pending orders from TikTok
      const pendingOrders = await this.fetchPendingOrders();

      // Extract order IDs
      const orderIds = pendingOrders.map(order => order.id);

      if (orderIds.length === 0) {
        return {
          totalOrders: 0,
          successCount: 0,
          failureCount: 0,
          results: [],
          errors: [],
        };
      }

      // Route all pending orders
      return await this.routeOrders(orderIds);
    } catch (error) {
      return {
        totalOrders: 0,
        successCount: 0,
        failureCount: 0,
        results: [],
        errors: [
          {
            orderId: 'N/A',
            stage: 'fetch',
            code: ErrorCode.TIKTOK_API_ERROR,
            message: `Failed to fetch pending orders: ${error instanceof Error ? error.message : 'Unknown error'}`,
            details: error,
          },
        ],
      };
    }
  }

  /**
   * Fetch all pending orders from TikTok Shop
   *
   * Internal helper method to fetch orders with AWAITING_SHIPMENT or AWAITING_COLLECTION status
   */
  private async fetchPendingOrders(): Promise<TikTokOrder[]> {
    const allOrders: TikTokOrder[] = [];

    const targetStatuses = [
      TikTokOrderStatus.AWAITING_SHIPMENT,
      TikTokOrderStatus.AWAITING_COLLECTION,
    ];

    // Fetch orders for each target status
    for (const status of targetStatuses) {
      let hasMore = true;
      let pageToken: string | undefined;

      while (hasMore) {
        const response = await this.tiktokClient.getOrders({
          order_status: status,
          page_size: 50,
          page_token: pageToken,
        });

        allOrders.push(...response.orders);

        hasMore = response.more;
        pageToken = response.next_page_token;

        // Safety check to prevent infinite loops
        if (!pageToken && hasMore) {
          break;
        }
      }
    }

    return allOrders;
  }

  /**
   * Update router configuration
   */
  updateConfig(config: Partial<OrderRouterConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Get current router configuration
   */
  getConfig(): Required<OrderRouterConfig> {
    return { ...this.config };
  }
}

/**
 * Create a new order router instance
 */
export function createOrderRouter(
  dependencies: OrderRouterDependencies,
  config?: OrderRouterConfig
): OrderRouter {
  return new OrderRouter(dependencies, config);
}
