/**
 * Order Validator - Validates TikTok orders and normalizes addresses for MCF
 *
 * Features:
 * - Validates required order fields
 * - Normalizes addresses to meet Amazon MCF requirements
 * - Checks for invalid data formats
 * - Provides clear validation error messages
 */
import type { TikTokOrder, NormalizedTikTokOrder } from '../types/tiktok-order';
import type { Address } from '../types/common';
export interface ValidationError {
    field: string;
    message: string;
    code: string;
}
export interface ValidationWarning {
    field: string;
    message: string;
}
export interface OrderValidationResult {
    valid: boolean;
    errors: ValidationError[];
    warnings?: ValidationWarning[];
    normalizedOrder?: NormalizedTikTokOrder;
    normalizedAddress?: Address;
}
export interface ValidatorConfig {
    strictMode?: boolean;
    maxAddressLength?: number;
    requiredPhoneNumber?: boolean;
    allowedCountries?: string[];
}
/**
 * OrderValidator validates TikTok orders and normalizes addresses for Amazon MCF
 */
export declare class OrderValidator {
    private config;
    constructor(config?: ValidatorConfig);
    /**
     * Validate a TikTok order and normalize data for MCF
     */
    validateOrder(order: TikTokOrder): OrderValidationResult;
    /**
     * Validate and normalize address for Amazon MCF
     */
    validateAddress(address: TikTokOrder['recipient_address']): {
        errors: ValidationError[];
        warnings?: ValidationWarning[];
        normalizedAddress?: Address;
    };
    /**
     * Normalize address to meet Amazon MCF requirements
     */
    private normalizeAddress;
    /**
     * Normalize TikTok order to internal format
     */
    private normalizeOrder;
}
/**
 * Create a new order validator instance
 */
export declare function createOrderValidator(config?: ValidatorConfig): OrderValidator;
//# sourceMappingURL=order-validator.d.ts.map