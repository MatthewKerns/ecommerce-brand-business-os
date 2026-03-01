# QA Fix Request

**Status**: REJECTED
**Date**: 2025-02-26T08:30:00Z
**QA Session**: 1

## Critical Issues to Fix

### 1. E2E Test TypeScript Compilation Errors
**Problem**: E2E test file uses incorrect MCFConnector constructor signature and property names
**Location**: `tests/e2e/order-routing-e2e.test.ts:44-85, 133-135, 209, 214-215`
**Required Fix**:

**File: tests/e2e/order-routing-e2e.test.ts**

**Change 1 - Lines 43-51 (Constructor):**
```typescript
// CURRENT (WRONG):
connector = new MCFConnector({
  tiktokShop: config.tiktokShop,
  amazonMCF: config.amazonMCF,
  connector: {
    ...config.connector,
    enableInventorySync: true,
    enableTrackingSyncScheduler: false,
  },
});

// SHOULD BE:
connector = new MCFConnector({
  config: config,
  enableInventorySync: true,
  enableTrackingSyncScheduler: false,
});
```

**Change 2 - Lines 56-57, 76-78, 82-84 (testConnections return type):**
```typescript
// CURRENT (WRONG):
expect(connections.tiktok.success).toBe(true);
expect(connections.tiktok.error).toBeUndefined();
expect(connections.amazon.success).toBe(true);
expect(connections.amazon.error).toBeUndefined();

// SHOULD BE:
expect(connections.tiktok).toBe(true);
expect(connections.amazon).toBe(true);
```

**Change 3 - Lines 133-135 (warnings property):**
```typescript
// CURRENT (WRONG):
if (firstResult.warnings && firstResult.warnings.length > 0) {
  console.log(`\nWarnings for order ${firstResult.orderId}:`);
  firstResult.warnings.forEach(w => console.log(`  - ${w.message}`));
}

// SHOULD BE:
// Remove this block - OrderRoutingResult doesn't have warnings at top level
// Warnings are in successResult.warnings if needed
if (firstResult.success && firstResult.successResult?.warnings?.length) {
  console.log(`\nWarnings for order ${firstResult.orderId}:`);
  firstResult.successResult.warnings.forEach((w: any) => console.log(`  - ${w.message}`));
}
```

**Change 4 - Line 209 (checkInventory signature):**
```typescript
// CURRENT (WRONG):
const inventoryResult = await connector.checkInventory([testSku]);

// SHOULD BE:
const inventoryResult = await connector.checkInventory(testSku, 1);
```

**Change 5 - Lines 214-215 (inventory result properties):**
```typescript
// CURRENT (WRONG):
if (inventoryResult.success) {
  console.log(`✓ Inventory available: ${inventoryResult.available} units`);
}

// SHOULD BE:
if (inventoryResult.sufficient) {
  console.log(`✓ Inventory available: ${inventoryResult.available} units`);
}
```

**Verification**:
- Run `npx tsc --noEmit` - should pass with 0 errors
- Run `npm test -- e2e` - should compile successfully (tests may be skipped without sandbox credentials)

---

### 2. Unit Test Mock Data Structure Mismatch
**Problem**: TikTokShopClient.getOrderDetail mocks return wrapped object `{ order: {...} }` instead of direct order object
**Location**: `src/core/__tests__/order-router.test.ts:273, 361, 386, 429, 471, 516, 558, 615, 677, 736, 786`
**Required Fix**:

**File: src/core/__tests__/order-router.test.ts**

Find all instances of:
```typescript
mockTikTokClient.getOrderDetail.mockResolvedValue({ order: tiktokOrder });
```

Replace with:
```typescript
mockTikTokClient.getOrderDetail.mockResolvedValue(tiktokOrder);
```

**Specific line numbers to fix:**
- Line 273
- Line 361
- Line 386
- Line 429
- Line 471
- Line 516
- Line 558
- Line 615
- Line 677
- Line 736
- Line 786

**Verification**: Run `npm test -- order-router.test` - test "should successfully route an order through the full pipeline" should pass

---

### 3. Unit Test Inventory Check Error Stage
**Problem**: Test expects MCF creation error but mock throws error during inventory check
**Location**: `src/core/__tests__/order-router.test.ts:513-549`
**Required Fix**:

**File: src/core/__tests__/order-router.test.ts**

**Around line 513-527 (setup section):**
```typescript
// CURRENT test setup:
it('should handle MCF creation failure', async () => {
  const orderId = 'TEST123';
  const tiktokOrder = createValidTikTokOrder(orderId);
  const normalizedAddress = createNormalizedAddress();
  const mcfRequest = createMCFOrderRequest();
  const error = new Error('MCF API error: insufficient inventory');

  mockTikTokClient.getOrderDetail.mockResolvedValue({ order: tiktokOrder });  // Fix #1: remove { order: }
  mockValidator.validateOrder.mockReturnValue({
    valid: true,
    errors: [],
    warnings: [],
    normalizedOrder: { ...tiktokOrder, recipient_address: normalizedAddress },
  });
  mockTransformer.transformOrder.mockReturnValue({
    success: true,
    mcfOrder: mcfRequest,
    warnings: [],
  });
  // Missing: inventory check mock should PASS
  // Missing: MCF creation should FAIL
  mockAmazonClient.createFulfillmentOrder.mockRejectedValue(error);
```

**SHOULD BE:**
```typescript
it('should handle MCF creation failure', async () => {
  const orderId = 'TEST123';
  const tiktokOrder = createValidTikTokOrder(orderId);
  const normalizedAddress = createNormalizedAddress();
  const mcfRequest = createMCFOrderRequest();
  const error = new Error('MCF API error: insufficient inventory');

  mockTikTokClient.getOrderDetail.mockResolvedValue(tiktokOrder);  // ✅ Fixed
  mockValidator.validateOrder.mockReturnValue({
    valid: true,
    errors: [],
    warnings: [],
    normalizedOrder: { ...tiktokOrder, recipient_address: normalizedAddress },
  });
  mockTransformer.transformOrder.mockReturnValue({
    success: true,
    mcfOrder: mcfRequest,
    warnings: [],
  });
  // ✅ ADD: Make inventory check pass
  mockInventorySync.checkInventoryBatch.mockResolvedValue({
    successCount: 1,
    insufficientCount: 0,
    lowStockCount: 0,
    errorCount: 0,
    results: [
      {
        sku: 'AMAZON-SKU-123',
        available: 100,
        requested: 2,
        sufficient: true,
        lowStock: false,
        cached: false,
      },
    ],
    errors: [],
  });
  // ✅ MCF creation should fail
  mockAmazonClient.createFulfillmentOrder.mockRejectedValue(error);
```

**Verification**: Run `npm test -- order-router.test` - test "should handle MCF creation failure" should pass

---

### 4. Resource Leak - Jest Worker Process Not Exiting
**Problem**: TrackingSync scheduler `setInterval` not cleaned up in tests
**Location**: Test files using TrackingSync with scheduler enabled
**Required Fix**:

**Option 1 - Add cleanup in tracking-sync.test.ts:**
```typescript
afterEach(async () => {
  // Stop scheduler if running
  if (trackingSync && typeof trackingSync.stopScheduler === 'function') {
    trackingSync.stopScheduler();
  }
});

afterAll(() => {
  jest.clearAllTimers();
});
```

**Option 2 - Use fake timers:**
```typescript
beforeEach(() => {
  jest.useFakeTimers();
});

afterEach(() => {
  jest.runOnlyPendingTimers();
  jest.useRealTimers();
});
```

**Verification**: Run `npm test` - should complete without "worker process has failed to exit gracefully" warning

---

## After Fixes

Once all fixes are complete:

1. **Verify TypeScript compilation:**
   ```bash
   cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/05-mcf-connector-integration/implementation
   npx tsc --noEmit
   ```
   Expected: 0 errors

2. **Run unit tests:**
   ```bash
   npm test
   ```
   Expected: All tests pass (159/159), no worker process warnings

3. **Run specific test suites:**
   ```bash
   npm test -- order-router.test
   npm test -- e2e
   ```
   Expected: All tests compile and pass

4. **Commit fixes:**
   ```bash
   git add -A
   git commit -m "fix: correct E2E test type errors and unit test mock structure (qa-requested)"
   ```

5. **QA will automatically re-run validation**

---

## Summary

**Critical Issues:** 4
**Affected Files:** 2
- `tests/e2e/order-routing-e2e.test.ts` (TypeScript compilation errors)
- `src/core/__tests__/order-router.test.ts` (mock structure and test setup)

**Estimated Fix Time:** 15-20 minutes

All issues are straightforward fixes related to test implementation, not production code. The core functionality is correct - only test files need updates.
