#!/usr/bin/env tsx
/**
 * Manual E2E Verification Script
 *
 * This script provides step-by-step verification of the MCF Connector
 * with real TikTok Shop and Amazon MCF sandbox environments.
 *
 * Usage:
 *   npm run build && tsx scripts/verify-e2e.ts
 *
 * Or with specific steps:
 *   tsx scripts/verify-e2e.ts --step=connections
 *   tsx scripts/verify-e2e.ts --step=orders
 *   tsx scripts/verify-e2e.ts --step=inventory
 *   tsx scripts/verify-e2e.ts --step=tracking
 *   tsx scripts/verify-e2e.ts --step=full
 */

import { MCFConnector } from '../src/index';
import { loadConfig } from '../src/config';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message: string, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function logStep(step: string) {
  log(`\n${'='.repeat(60)}`, colors.cyan);
  log(`  ${step}`, colors.bright);
  log('='.repeat(60), colors.cyan);
}

function logSuccess(message: string) {
  log(`✓ ${message}`, colors.green);
}

function logError(message: string) {
  log(`✗ ${message}`, colors.red);
}

function logWarning(message: string) {
  log(`⚠ ${message}`, colors.yellow);
}

function logInfo(message: string) {
  log(`ℹ ${message}`, colors.blue);
}

async function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function verifyConnections(connector: MCFConnector) {
  logStep('Step 1: Verify API Connections');

  try {
    const result = await connector.testConnections();

    // TikTok Shop connection
    if (result.tiktok.success) {
      logSuccess('TikTok Shop API connection successful');
    } else {
      logError(`TikTok Shop API connection failed: ${result.tiktok.error}`);
      return false;
    }

    // Amazon MCF connection
    if (result.amazon.success) {
      logSuccess('Amazon MCF API connection successful');
    } else {
      logError(`Amazon MCF API connection failed: ${result.amazon.error}`);
      return false;
    }

    logSuccess('All API connections verified');
    return true;
  } catch (error) {
    logError(`Connection verification failed: ${error instanceof Error ? error.message : String(error)}`);
    return false;
  }
}

async function verifyOrderDetection(connector: MCFConnector) {
  logStep('Step 2: Verify Order Detection and Routing');

  try {
    logInfo('Fetching pending TikTok Shop orders...');
    const result = await connector.routePendingOrders();

    log(`\nOrder Detection Results:`, colors.cyan);
    console.log(`  Total Orders: ${result.totalOrders}`);
    console.log(`  Successfully Routed: ${result.successCount}`);
    console.log(`  Failed: ${result.failedCount}`);

    if (result.totalOrders === 0) {
      logWarning('No pending orders found in TikTok Shop');
      logInfo('Create a test order in TikTok Shop sandbox with status AWAITING_SHIPMENT');
      return false;
    }

    // Show detailed results
    log(`\nDetailed Results:`, colors.cyan);
    result.results.forEach((r, i) => {
      console.log(`\n  Order ${i + 1}: ${r.orderId}`);

      if (r.success) {
        logSuccess(`    Status: SUCCESS`);
        const successResult = r as any;
        if (successResult.mcfOrderId) {
          console.log(`    MCF Order ID: ${successResult.mcfOrderId}`);
        }
        if (r.warnings && r.warnings.length > 0) {
          console.log(`    Warnings:`);
          r.warnings.forEach(w => logWarning(`      - ${w.message}`));
        }
      } else {
        logError(`    Status: FAILED`);
        if (r.error) {
          console.log(`    Stage: ${r.error.stage}`);
          console.log(`    Code: ${r.error.code}`);
          console.log(`    Message: ${r.error.message}`);
        }
      }
    });

    if (result.successCount > 0) {
      logSuccess(`Successfully routed ${result.successCount} order(s)`);
      return true;
    } else {
      logError('No orders were successfully routed');
      logInfo('Check the error details above and fix the issues');
      return false;
    }
  } catch (error) {
    logError(`Order detection failed: ${error instanceof Error ? error.message : String(error)}`);
    return false;
  }
}

async function verifyInventory(connector: MCFConnector) {
  logStep('Step 3: Verify Inventory Sync');

  try {
    const testSkus = ['TEST-SKU-001', 'TEST-SKU-002'];

    logInfo(`Checking inventory for SKUs: ${testSkus.join(', ')}`);
    const result = await connector.checkInventory(testSkus);

    if (result.success) {
      log(`\nInventory Results:`, colors.cyan);
      result.summaries.forEach(summary => {
        console.log(`\n  SKU: ${summary.sellerSku}`);
        console.log(`    Total Quantity: ${summary.totalQuantity}`);
        console.log(`    Fulfillable: ${summary.fulfillableQuantity}`);
        console.log(`    Reserved: ${summary.reservedQuantity || 0}`);
        console.log(`    Inbound: ${summary.inboundQuantity || 0}`);

        if (summary.fulfillableQuantity === 0) {
          logWarning(`    Low/zero stock!`);
        } else if (summary.fulfillableQuantity < 10) {
          logWarning(`    Low stock warning (< 10 units)`);
        } else {
          logSuccess(`    Stock level OK`);
        }
      });

      logSuccess('Inventory check completed');
    } else {
      logError(`Inventory check failed: ${result.error?.message}`);
      logInfo('This is expected if the test SKUs do not exist in Amazon FBA inventory');
    }

    // Check for low stock SKUs
    logInfo('\nChecking for low stock SKUs...');
    const lowStockSkus = await connector.getLowStockSkus();

    if (lowStockSkus.length === 0) {
      logSuccess('No low stock SKUs found (all SKUs have sufficient stock)');
    } else {
      logWarning(`Found ${lowStockSkus.length} low stock SKU(s):`);
      lowStockSkus.forEach(sku => {
        console.log(`  - ${sku.sku}: ${sku.fulfillableQuantity} units`);
      });
    }

    return true;
  } catch (error) {
    logError(`Inventory verification failed: ${error instanceof Error ? error.message : String(error)}`);
    logInfo('Inventory checks may fail in sandbox environments - this is not critical');
    return true; // Don't fail the whole verification for inventory issues
  }
}

async function verifyTracking(connector: MCFConnector) {
  logStep('Step 4: Verify Tracking Sync');

  try {
    logInfo('Syncing tracking information from MCF to TikTok Shop...');
    const result = await connector.syncAllTracking();

    log(`\nTracking Sync Results:`, colors.cyan);
    console.log(`  Total Orders: ${result.totalOrders}`);
    console.log(`  Synced: ${result.syncedCount}`);
    console.log(`  Failed: ${result.failedCount}`);
    console.log(`  No Tracking Available: ${result.noTrackingCount}`);
    console.log(`  Already Synced: ${result.alreadySyncedCount}`);

    if (result.results.length > 0) {
      log(`\nDetailed Results:`, colors.cyan);
      result.results.forEach((r, i) => {
        console.log(`\n  Order ${i + 1}: ${r.orderId}`);

        if (r.synced) {
          logSuccess(`    Status: SYNCED`);
          console.log(`    Tracking Number: ${r.trackingNumber}`);
          console.log(`    Carrier: ${r.carrier || 'N/A'}`);
          if (r.updatedAt) {
            console.log(`    Updated At: ${new Date(r.updatedAt).toLocaleString()}`);
          }
        } else if (r.error) {
          logError(`    Status: FAILED`);
          console.log(`    Error: ${r.error}`);
        } else {
          logWarning(`    Status: NO TRACKING AVAILABLE`);
          logInfo(`      Tracking numbers will appear once MCF ships the order`);
        }
      });
    }

    if (result.syncedCount > 0) {
      logSuccess(`Successfully synced ${result.syncedCount} tracking number(s)`);
    } else if (result.noTrackingCount > 0) {
      logWarning('No tracking numbers available yet');
      logInfo('Wait for MCF to ship the orders (this can take hours in sandbox)');
    }

    return true;
  } catch (error) {
    logError(`Tracking sync failed: ${error instanceof Error ? error.message : String(error)}`);
    return false;
  }
}

async function verifyFullFlow(connector: MCFConnector) {
  logStep('Full End-to-End Verification Flow');

  log('\nThis will run the complete order routing flow:', colors.cyan);
  log('  1. Fetch pending TikTok orders', colors.cyan);
  log('  2. Validate and transform orders', colors.cyan);
  log('  3. Create MCF fulfillment orders', colors.cyan);
  log('  4. Check inventory', colors.cyan);
  log('  5. Wait for MCF processing', colors.cyan);
  log('  6. Sync tracking information\n', colors.cyan);

  // Step 1: Route orders
  logInfo('Step 1/6: Routing pending orders...');
  const routeResult = await connector.routePendingOrders();

  console.log(`  Orders detected: ${routeResult.totalOrders}`);
  console.log(`  Successfully routed: ${routeResult.successCount}`);
  console.log(`  Failed: ${routeResult.failedCount}`);

  if (routeResult.totalOrders === 0) {
    logWarning('No orders to process');
    logInfo('Create a test order in TikTok Shop sandbox to test the full flow');
    return false;
  }

  // Step 2: Show successful orders
  if (routeResult.successCount > 0) {
    logSuccess(`Step 1/6 Complete: ${routeResult.successCount} order(s) routed`);

    log('\nSuccessfully Routed Orders:', colors.cyan);
    routeResult.results
      .filter(r => r.success)
      .forEach(r => {
        const successResult = r as any;
        console.log(`  - TikTok Order: ${r.orderId}`);
        console.log(`    MCF Order: ${successResult.mcfOrderId || 'N/A'}`);
      });
  } else {
    logError('Step 1/6 Failed: No orders routed successfully');
    return false;
  }

  // Step 3: Check inventory
  logInfo('\nStep 2/6: Checking inventory...');
  try {
    const testSkus = ['TEST-SKU-001'];
    const inventoryResult = await connector.checkInventory(testSkus);

    if (inventoryResult.success) {
      logSuccess('Step 2/6 Complete: Inventory check passed');
      inventoryResult.summaries.forEach(s => {
        console.log(`  ${s.sellerSku}: ${s.fulfillableQuantity} units available`);
      });
    } else {
      logWarning('Step 2/6: Inventory check completed with warnings');
    }
  } catch (error) {
    logWarning('Step 2/6: Inventory check skipped (not critical)');
  }

  // Step 4: Wait for MCF processing
  logInfo('\nStep 3/6: Waiting for MCF to process orders...');
  logInfo('Waiting 15 seconds (in production, this could take hours)...');
  await sleep(15000);
  logSuccess('Step 3/6 Complete: Wait finished');

  // Step 5: Sync tracking
  logInfo('\nStep 4/6: Syncing tracking information...');
  const trackingResult = await connector.syncAllTracking();

  console.log(`  Synced: ${trackingResult.syncedCount}`);
  console.log(`  No tracking yet: ${trackingResult.noTrackingCount}`);
  console.log(`  Failed: ${trackingResult.failedCount}`);

  if (trackingResult.syncedCount > 0) {
    logSuccess('Step 4/6 Complete: Tracking synced successfully');
  } else if (trackingResult.noTrackingCount > 0) {
    logWarning('Step 4/6: No tracking available yet');
    logInfo('Tracking numbers will appear once MCF ships the orders');
  } else {
    logError('Step 4/6: Tracking sync failed');
  }

  // Summary
  logStep('End-to-End Verification Summary');

  const summary = {
    ordersDetected: routeResult.totalOrders,
    ordersRouted: routeResult.successCount,
    ordersFailed: routeResult.failedCount,
    trackingSynced: trackingResult.syncedCount,
    trackingPending: trackingResult.noTrackingCount,
  };

  log('\nResults:', colors.cyan);
  console.log(`  Orders Detected: ${summary.ordersDetected}`);
  console.log(`  Orders Routed to MCF: ${summary.ordersRouted}`);
  console.log(`  Orders Failed: ${summary.ordersFailed}`);
  console.log(`  Tracking Synced: ${summary.trackingSynced}`);
  console.log(`  Tracking Pending: ${summary.trackingPending}`);

  if (summary.ordersRouted > 0) {
    log('\n' + '='.repeat(60), colors.green);
    logSuccess('END-TO-END VERIFICATION PASSED');
    log('='.repeat(60) + '\n', colors.green);
    return true;
  } else {
    log('\n' + '='.repeat(60), colors.red);
    logError('END-TO-END VERIFICATION FAILED');
    log('='.repeat(60) + '\n', colors.red);
    return false;
  }
}

async function main() {
  log('\n' + '='.repeat(60), colors.bright);
  log('  MCF Connector - End-to-End Verification', colors.bright);
  log('='.repeat(60) + '\n', colors.bright);

  // Parse command line arguments
  const args = process.argv.slice(2);
  const stepArg = args.find(arg => arg.startsWith('--step='));
  const step = stepArg ? stepArg.split('=')[1] : 'full';

  // Load configuration
  logInfo('Loading configuration from environment...');
  let config;
  try {
    config = loadConfig();
    logSuccess('Configuration loaded successfully');
  } catch (error) {
    logError(`Failed to load configuration: ${error instanceof Error ? error.message : String(error)}`);
    logInfo('Make sure you have a .env file with valid credentials');
    process.exit(1);
  }

  // Initialize connector
  logInfo('Initializing MCF Connector...');
  const connector = new MCFConnector({
    tiktokShop: config.tiktokShop,
    amazonMCF: config.amazonMCF,
    connector: {
      ...config.connector,
      enableInventorySync: true,
      enableTrackingSyncScheduler: false,
    },
  });
  logSuccess('MCF Connector initialized');

  let success = true;

  try {
    switch (step) {
      case 'connections':
        success = await verifyConnections(connector);
        break;

      case 'orders':
        success = await verifyConnections(connector);
        if (success) success = await verifyOrderDetection(connector);
        break;

      case 'inventory':
        success = await verifyConnections(connector);
        if (success) success = await verifyInventory(connector);
        break;

      case 'tracking':
        success = await verifyConnections(connector);
        if (success) success = await verifyTracking(connector);
        break;

      case 'full':
      default:
        success = await verifyConnections(connector);
        if (success) success = await verifyFullFlow(connector);
        break;
    }
  } finally {
    // Cleanup
    await connector.shutdown();
  }

  // Exit with appropriate code
  process.exit(success ? 0 : 1);
}

// Run the verification
main().catch(error => {
  logError(`Unexpected error: ${error instanceof Error ? error.message : String(error)}`);
  if (error instanceof Error && error.stack) {
    console.error(error.stack);
  }
  process.exit(1);
});
