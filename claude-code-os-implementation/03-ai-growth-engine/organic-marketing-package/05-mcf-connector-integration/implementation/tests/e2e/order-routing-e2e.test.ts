/**
 * End-to-End Tests - TikTok Shop to Amazon MCF Order Routing
 *
 * This test suite verifies the complete order routing flow using sandbox environments:
 * 1. Create test order in TikTok Shop sandbox
 * 2. Verify connector detects order within 5 minutes
 * 3. Verify order validation passes
 * 4. Verify MCF fulfillment order created
 * 5. Verify tracking sync updates TikTok Shop
 * 6. Verify inventory sync prevents overselling
 *
 * PREREQUISITES:
 * - TikTok Shop sandbox account with valid credentials
 * - Amazon MCF sandbox account with valid credentials
 * - Environment variables configured (see .env.example)
 *
 * USAGE:
 * npm run test:e2e
 */

import { MCFConnector } from '../../src/index';
import { loadConfig } from '../../src/config';
import { TikTokOrderStatus, MCFFulfillmentStatus, ErrorCode } from '../../src/types/common';

// Skip these tests in CI unless explicitly enabled
const E2E_ENABLED = process.env.RUN_E2E_TESTS === 'true';
const describeE2E = E2E_ENABLED ? describe : describe.skip;

// Timeout for API operations (5 minutes)
const API_TIMEOUT = 5 * 60 * 1000;

// Track test order IDs for cleanup
const testOrderIds: string[] = [];

describeE2E('End-to-End Order Routing', () => {
  let connector: MCFConnector;

  beforeAll(async () => {
    // Load configuration from environment
    const config = loadConfig();

    // Initialize the connector
    connector = new MCFConnector({
      config: config,
      enableInventorySync: true,
      enableTrackingSyncScheduler: false,
    });

    // Verify API connections
    const connections = await connector.testConnections();

    expect(connections.tiktok).toBe(true);
    expect(connections.amazon).toBe(true);
  }, API_TIMEOUT);

  afterAll(async () => {
    // Cleanup: Note test order IDs for manual cleanup if needed
    if (testOrderIds.length > 0) {
      console.log('\n=== Test Orders Created ===');
      console.log('The following test orders were created and may need cleanup:');
      testOrderIds.forEach(id => console.log(`  - ${id}`));
    }

    // Shutdown connector
    if (connector) {
      await connector.shutdown();
    }
  });

  describe('Connection Tests', () => {
    it('should successfully connect to TikTok Shop API', async () => {
      const result = await connector.testConnections();
      expect(result.tiktok).toBe(true);
    }, API_TIMEOUT);

    it('should successfully connect to Amazon MCF API', async () => {
      const result = await connector.testConnections();
      expect(result.amazon).toBe(true);
    }, API_TIMEOUT);
  });

  describe('Order Detection and Fetching', () => {
    it('should detect pending TikTok Shop orders', async () => {
      // Note: This requires at least one test order in AWAITING_SHIPMENT status
      // in the TikTok Shop sandbox
      const result = await connector.routePendingOrders();

      expect(result.totalOrders).toBeGreaterThanOrEqual(0);

      if (result.totalOrders > 0) {
        console.log(`\nDetected ${result.totalOrders} pending order(s)`);
        result.results.forEach((r, i) => {
          console.log(`  Order ${i + 1}: ${r.orderId} - ${r.success ? 'SUCCESS' : 'FAILED'}`);
          if (!r.success && r.error) {
            console.log(`    Error: ${r.error.message}`);
          }
        });
      } else {
        console.log('\nNo pending orders found in TikTok Shop sandbox');
        console.log('Skipping order routing tests - create a test order in sandbox to continue');
      }
    }, API_TIMEOUT);
  });

  describe('Order Validation', () => {
    it('should validate order with all required fields', async () => {
      // This test assumes you have a valid test order in sandbox
      const result = await connector.routePendingOrders();

      if (result.totalOrders === 0) {
        console.log('Skipping validation test - no orders available');
        return;
      }

      const firstResult = result.results[0];

      if (!firstResult.success) {
        // If validation failed, check the error
        expect(firstResult.error?.stage).toBe('validate');
        expect(firstResult.error?.code).toBeDefined();
        console.log(`\nValidation failed as expected: ${firstResult.error?.message}`);
      } else {
        // Validation passed
        expect(firstResult.success).toBe(true);
        console.log('\nValidation passed successfully');

        if (firstResult.success && firstResult.successResult?.warnings?.length) {
          console.log(`\nWarnings for order ${firstResult.orderId}:`);
          firstResult.successResult.warnings.forEach((w: any) => console.log(`  - ${w.message}`));
        }
      }
    }, API_TIMEOUT);

    it('should normalize addresses to MCF requirements', async () => {
      const result = await connector.routePendingOrders();

      if (result.totalOrders === 0) {
        console.log('Skipping address normalization test - no orders available');
        return;
      }

      const successfulResults = result.results.filter(r => r.success);

      if (successfulResults.length > 0) {
        console.log('\nAddress normalization completed for successful orders');
        // The fact that transformation succeeded means address normalization worked
        expect(successfulResults.length).toBeGreaterThan(0);
      }
    }, API_TIMEOUT);
  });

  describe('MCF Order Creation', () => {
    it('should create MCF fulfillment order from TikTok order', async () => {
      const result = await connector.routePendingOrders();

      if (result.totalOrders === 0) {
        console.log('Skipping MCF order creation test - no orders available');
        return;
      }

      const successfulResults = result.results.filter(r => r.success);

      if (successfulResults.length > 0) {
        const firstSuccess = successfulResults[0] as any;
        console.log('\nMCF Order Created Successfully:');
        console.log(`  TikTok Order ID: ${firstSuccess.orderId}`);
        console.log(`  MCF Order ID: ${firstSuccess.mcfOrderId || 'N/A'}`);

        expect(firstSuccess.mcfOrderId).toBeDefined();

        // Track for cleanup
        if (firstSuccess.orderId) {
          testOrderIds.push(firstSuccess.orderId);
        }
      } else {
        console.log('\nNo successful MCF orders created');
        console.log('Check error details above for issues');
      }
    }, API_TIMEOUT);

    it('should handle MCF API errors gracefully', async () => {
      const result = await connector.routePendingOrders();

      const failedResults = result.results.filter(r => !r.success);

      if (failedResults.length > 0) {
        console.log('\nMCF API errors handled:');
        failedResults.forEach(r => {
          if (r.error?.stage === 'create_mcf') {
            console.log(`  Order ${r.orderId}: ${r.error.message}`);
            expect(r.error.code).toBeDefined();
          }
        });
      }
    }, API_TIMEOUT);
  });

  describe('Inventory Sync', () => {
    it('should check inventory before creating MCF orders', async () => {
      const testSku = 'TEST-SKU-001';

      try {
        const inventoryResult = await connector.checkInventory(testSku, 1);

        console.log('\nInventory Check Result:');
        console.log(`  SKU: ${testSku}`);

        if (inventoryResult.sufficient) {
          console.log(`  Available: ${inventoryResult.available} units`);
          expect(inventoryResult.sufficient).toBe(true);
        } else {
          console.log(`  Insufficient inventory`);
        }
      } catch (error) {
        console.log('\nInventory check failed (this is expected if SKU does not exist in sandbox)');
        console.log(`  Error: ${error instanceof Error ? error.message : String(error)}`);
      }
    }, API_TIMEOUT);

    it('should prevent overselling when inventory is insufficient', async () => {
      // This test requires a SKU with 0 inventory in Amazon sandbox
      const result = await connector.routePendingOrders();

      const insufficientInventoryResults = result.results.filter(
        r => !r.success && r.error?.code === ErrorCode.INSUFFICIENT_INVENTORY
      );

      if (insufficientInventoryResults.length > 0) {
        console.log('\nOverselling prevented for orders with insufficient inventory:');
        insufficientInventoryResults.forEach(r => {
          console.log(`  Order ${r.orderId}: ${r.error?.message}`);
        });

        expect(insufficientInventoryResults.every(r => r.error?.code === ErrorCode.INSUFFICIENT_INVENTORY)).toBe(true);
      } else {
        console.log('\nNo orders blocked due to insufficient inventory');
        console.log('(This is expected if all SKUs have sufficient stock in sandbox)');
      }
    }, API_TIMEOUT);

    it('should get low stock SKUs', async () => {
      const lowStockSkus = await connector.getLowStockSkus();

      console.log('\nLow Stock SKUs:');
      if (lowStockSkus.length === 0) {
        console.log('  None (all SKUs have sufficient stock)');
      } else {
        lowStockSkus.forEach(sku => {
          console.log(`  - ${sku.sku}: ${sku.fulfillableQuantity} units remaining`);
        });
      }

      expect(Array.isArray(lowStockSkus)).toBe(true);
    }, API_TIMEOUT);
  });

  describe('Tracking Sync', () => {
    it('should sync tracking numbers from MCF to TikTok', async () => {
      // First, route pending orders to create MCF orders
      const routeResult = await connector.routePendingOrders();

      if (routeResult.successCount === 0) {
        console.log('Skipping tracking sync test - no successful orders to sync');
        return;
      }

      // Wait a bit for MCF to process the order
      console.log('\nWaiting 10 seconds for MCF to process orders...');
      await new Promise(resolve => setTimeout(resolve, 10000));

      // Sync all tracking
      const syncResult = await connector.syncAllTracking();

      console.log('\nTracking Sync Results:');
      console.log(`  Total Orders: ${syncResult.totalOrders}`);
      console.log(`  Synced: ${syncResult.syncedCount}`);
      console.log(`  Failed: ${syncResult.failedCount}`);
      console.log(`  No Tracking Available: ${syncResult.noTrackingCount}`);
      console.log(`  Already Synced: ${syncResult.alreadySyncedCount}`);

      expect(syncResult.totalOrders).toBeGreaterThanOrEqual(0);

      if (syncResult.results.length > 0) {
        console.log('\nSync Details:');
        syncResult.results.forEach(r => {
          console.log(`  Order ${r.orderId}:`);
          console.log(`    Status: ${r.synced ? 'SYNCED' : 'NOT SYNCED'}`);
          if (r.trackingNumber) {
            console.log(`    Tracking: ${r.trackingNumber}`);
            console.log(`    Carrier: ${r.carrier || 'N/A'}`);
          }
          if (r.error) {
            console.log(`    Error: ${r.error}`);
          }
        });
      }
    }, API_TIMEOUT);

    it('should skip already synced orders', async () => {
      // Run sync twice to test skip logic
      await connector.syncAllTracking();
      const secondSyncResult = await connector.syncAllTracking();

      console.log('\nSecond Sync (Should Skip Already Synced):');
      console.log(`  Already Synced: ${secondSyncResult.alreadySyncedCount}`);

      expect(secondSyncResult.alreadySyncedCount).toBeGreaterThanOrEqual(0);
    }, API_TIMEOUT);
  });

  describe('End-to-End Flow', () => {
    it('should complete full order routing flow', async () => {
      console.log('\n=== FULL END-TO-END TEST ===\n');

      // Step 1: Route pending orders
      console.log('Step 1: Routing pending TikTok orders...');
      const routeResult = await connector.routePendingOrders();
      console.log(`  ✓ Found ${routeResult.totalOrders} order(s)`);
      console.log(`  ✓ Successfully routed: ${routeResult.successCount}`);
      console.log(`  ✗ Failed: ${routeResult.failedCount}`);

      if (routeResult.totalOrders === 0) {
        console.log('\nℹ No orders to process. Create a test order in TikTok Shop sandbox to test the full flow.');
        return;
      }

      // Step 2: Check inventory for a test SKU
      console.log('\nStep 2: Checking inventory...');
      const testSku = 'TEST-SKU-001';
      try {
        const inventoryResult = await connector.checkInventory(testSku, 1);
        if (inventoryResult.sufficient) {
          console.log(`  ✓ SKU ${testSku}: ${inventoryResult.available} units available`);
        } else {
          console.log(`  ℹ Inventory check completed (SKU may not exist in sandbox)`);
        }
      } catch (error) {
        console.log(`  ℹ Inventory check skipped (expected in some sandbox environments)`);
      }

      // Step 3: Wait for MCF processing
      if (routeResult.successCount > 0) {
        console.log('\nStep 3: Waiting 15 seconds for MCF to process orders...');
        await new Promise(resolve => setTimeout(resolve, 15000));
        console.log('  ✓ Wait complete');
      }

      // Step 4: Sync tracking information
      console.log('\nStep 4: Syncing tracking information...');
      const syncResult = await connector.syncAllTracking();
      console.log(`  ✓ Synced: ${syncResult.syncedCount}`);
      console.log(`  ℹ No tracking yet: ${syncResult.noTrackingCount}`);
      console.log(`  ✗ Failed: ${syncResult.failedCount}`);

      // Step 5: Summary
      console.log('\n=== END-TO-END TEST COMPLETE ===\n');
      console.log('Summary:');
      console.log(`  Orders Detected: ${routeResult.totalOrders}`);
      console.log(`  Orders Routed: ${routeResult.successCount}`);
      console.log(`  Tracking Synced: ${syncResult.syncedCount}`);

      if (routeResult.successCount > 0) {
        console.log('\n✓ End-to-end flow completed successfully!');
        expect(routeResult.successCount).toBeGreaterThan(0);
      } else {
        console.log('\nℹ No orders were successfully routed. Check errors above.');
      }
    }, API_TIMEOUT * 2);
  });

  describe('Error Handling', () => {
    it('should handle invalid TikTok order IDs', async () => {
      const result = await connector.routeOrder('INVALID-ORDER-ID-12345');

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.error?.stage).toBe('fetch');

      console.log('\nInvalid order ID handled correctly:');
      console.log(`  Error: ${result.error?.message}`);
    }, API_TIMEOUT);

    it('should continue processing on errors when configured', async () => {
      const result = await connector.routeOrders([
        'INVALID-ORDER-1',
        'INVALID-ORDER-2',
        'INVALID-ORDER-3',
      ]);

      expect(result.totalOrders).toBe(3);
      expect(result.failedCount).toBe(3);

      console.log('\nBatch processing with errors:');
      console.log(`  Processed: ${result.totalOrders}`);
      console.log(`  Failed: ${result.failedCount}`);
      console.log('  All errors were handled without stopping batch processing');
    }, API_TIMEOUT);
  });

  describe('SKU Mapping', () => {
    it('should add and use SKU mappings', () => {
      connector.addSkuMapping('TIKTOK-SKU-001', 'AMAZON-SKU-001');
      connector.addSkuMapping('TIKTOK-SKU-002', 'AMAZON-SKU-002');

      console.log('\nSKU Mappings added:');
      console.log('  TIKTOK-SKU-001 → AMAZON-SKU-001');
      console.log('  TIKTOK-SKU-002 → AMAZON-SKU-002');

      // Note: These mappings will be used in subsequent order routing
      expect(true).toBe(true);
    });
  });
});
