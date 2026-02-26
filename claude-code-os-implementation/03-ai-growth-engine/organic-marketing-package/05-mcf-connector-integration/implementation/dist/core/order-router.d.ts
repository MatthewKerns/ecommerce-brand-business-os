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
import { ErrorCode } from '../types/common';
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
    inventorySync?: InventorySync;
}
/**
 * OrderRouter orchestrates the full order routing flow from TikTok to Amazon MCF
 */
export declare class OrderRouter {
    private config;
    private tiktokClient;
    private amazonClient;
    private validator;
    private transformer;
    private inventorySync?;
    constructor(dependencies: OrderRouterDependencies, config?: OrderRouterConfig);
    /**
     * Route a single TikTok order to Amazon MCF
     */
    routeOrder(orderId: string): Promise<OrderRoutingResult>;
    /**
     * Route multiple TikTok orders to Amazon MCF
     */
    routeOrders(orderIds: string[]): Promise<BatchRoutingResult>;
    /**
     * Route all pending TikTok orders to Amazon MCF
     *
     * Fetches all orders with AWAITING_SHIPMENT or AWAITING_COLLECTION status
     * and routes them to MCF.
     */
    routePendingOrders(): Promise<BatchRoutingResult>;
    /**
     * Fetch all pending orders from TikTok Shop
     *
     * Internal helper method to fetch orders with AWAITING_SHIPMENT or AWAITING_COLLECTION status
     */
    private fetchPendingOrders;
    /**
     * Update router configuration
     */
    updateConfig(config: Partial<OrderRouterConfig>): void;
    /**
     * Get current router configuration
     */
    getConfig(): Required<OrderRouterConfig>;
}
/**
 * Create a new order router instance
 */
export declare function createOrderRouter(dependencies: OrderRouterDependencies, config?: OrderRouterConfig): OrderRouter;
//# sourceMappingURL=order-router.d.ts.map