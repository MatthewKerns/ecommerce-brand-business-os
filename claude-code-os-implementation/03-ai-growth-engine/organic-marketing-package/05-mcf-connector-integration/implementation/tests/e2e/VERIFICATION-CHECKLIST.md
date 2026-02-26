# MCF Connector - End-to-End Verification Checklist

Use this checklist to verify all acceptance criteria are met before deploying to production.

## Date: ________________
## Tester: ________________
## Environment: ☐ Sandbox  ☐ Staging  ☐ Production

---

## Prerequisites

### TikTok Shop Setup
- [ ] TikTok Shop sandbox account configured
- [ ] Test app created with valid credentials
- [ ] OAuth tokens obtained (access token + refresh token)
- [ ] Test products created with SKUs
- [ ] Test shop ID verified

### Amazon MCF Setup
- [ ] Amazon Seller Central account configured
- [ ] SP-API developer application created
- [ ] LWA credentials obtained (client ID + secret)
- [ ] AWS credentials configured (access key + secret key)
- [ ] MCF inventory set up with test SKUs
- [ ] Seller ID and marketplace ID verified

### Environment Configuration
- [ ] `.env` file created from `.env.example`
- [ ] All required environment variables populated
- [ ] `RUN_E2E_TESTS=true` set for automated tests
- [ ] Dependencies installed (`npm install`)
- [ ] Project builds successfully (`npm run build`)

---

## Acceptance Criterion 1: Order Detection (< 5 minutes)

**Requirement:** New TikTok Shop orders automatically detected within 5 minutes

### Test Steps:
1. [ ] Create test order in TikTok Shop with status AWAITING_SHIPMENT
2. [ ] Record order creation time: _______________
3. [ ] Run: `npm run test:e2e` or `tsx scripts/verify-e2e.ts --step=orders`
4. [ ] Record order detection time: _______________
5. [ ] Calculate time difference: _______________

### Expected Results:
- [ ] Order detected in < 5 minutes
- [ ] Order ID matches test order
- [ ] Order status is AWAITING_SHIPMENT
- [ ] All order fields populated correctly

### Actual Results:
```
Orders detected: _______
Detection time: _______ minutes
Status: ☐ PASS  ☐ FAIL
```

### Notes:
```


```

---

## Acceptance Criterion 2: Order Validation and Transformation

**Requirement:** Order data validated and transformed for MCF requirements

### Test Steps:
1. [ ] Create test order with complete address information
2. [ ] Include order with US state name (e.g., "California")
3. [ ] Include order with phone number in various formats
4. [ ] Run order routing: `npm run test:e2e`

### Expected Results:
- [ ] Required fields validated (recipient name, address, phone, items)
- [ ] US state names converted to abbreviations (California → CA)
- [ ] Phone numbers normalized to E.164 format (+15550100)
- [ ] Address fields truncated to MCF limits
- [ ] Invalid orders rejected with clear error messages

### Actual Results:
```
Validation status: ☐ PASS  ☐ FAIL
Normalization status: ☐ PASS  ☐ FAIL
Error messages clear: ☐ YES  ☐ NO
```

### Sample Validated Order:
```
TikTok Order ID: _________________
Recipient Name: __________________
Address: _________________________
Phone: ___________________________
Items: ___________________________
```

### Notes:
```


```

---

## Acceptance Criterion 3: MCF Order Creation

**Requirement:** MCF fulfillment orders created with correct product mapping

### Test Steps:
1. [ ] Add SKU mapping: `connector.addSkuMapping('TIKTOK-SKU-001', 'AMAZON-SKU-001')`
2. [ ] Create test order with mapped SKU in TikTok Shop
3. [ ] Run order routing
4. [ ] Verify MCF order in Amazon Seller Central

### Expected Results:
- [ ] MCF fulfillment order created successfully
- [ ] TikTok SKU mapped to Amazon SKU correctly
- [ ] Shipping address matches normalized TikTok address
- [ ] Item quantities correct
- [ ] Shipping speed determined correctly from delivery option
- [ ] Order comment includes buyer message

### Actual Results:
```
TikTok Order ID: _________________
MCF Order ID: ____________________
SKU mapping correct: ☐ YES  ☐ NO
Address match: ☐ YES  ☐ NO
Quantities match: ☐ YES  ☐ NO
Status: ☐ PASS  ☐ FAIL
```

### Verification in Amazon Seller Central:
1. [ ] Go to Orders > Manage Multi-Channel Fulfillment Orders
2. [ ] Search for MCF Order ID: _________________
3. [ ] Verify order details match screenshot/notes below

### Notes:
```


```

---

## Acceptance Criterion 4: Tracking Sync (< 4 hours)

**Requirement:** Tracking numbers synced back to TikTok Shop within 4 hours of shipment

### Test Steps:
1. [ ] Wait for MCF to ship order (or simulate in sandbox)
2. [ ] Record shipment time: _______________
3. [ ] Run tracking sync: `tsx scripts/verify-e2e.ts --step=tracking`
4. [ ] Check TikTok Shop for tracking number
5. [ ] Record sync time: _______________
6. [ ] Calculate time difference: _______________

### Expected Results:
- [ ] Tracking number retrieved from MCF
- [ ] Tracking number updated in TikTok Shop
- [ ] Carrier information included
- [ ] Sync completes in < 4 hours
- [ ] Already-synced orders skipped on subsequent runs

### Actual Results:
```
Tracking number: _________________
Carrier: _________________________
Sync time: _______ hours
Status: ☐ PASS  ☐ FAIL
```

### Verification in TikTok Shop:
1. [ ] Go to Orders > Order List
2. [ ] Find order ID: _________________
3. [ ] Verify tracking information matches

### Notes:
```


```

---

## Acceptance Criterion 5: Failed Order Handling

**Requirement:** Failed orders flagged for manual review with clear error messages

### Test Steps:
1. [ ] Create order with invalid address (missing required field)
2. [ ] Create order with unmapped SKU
3. [ ] Create order with 0 inventory SKU
4. [ ] Run order routing
5. [ ] Review error messages

### Expected Results:
- [ ] Invalid address → INVALID_ADDRESS error with field name
- [ ] Unmapped SKU → Warning (order still processes with TikTok SKU)
- [ ] Zero inventory → INSUFFICIENT_INVENTORY error with SKU
- [ ] All errors include:
  - [ ] Error code
  - [ ] Clear message
  - [ ] Stage where error occurred (fetch/validate/transform/create_mcf)
  - [ ] Order ID for tracking

### Actual Results:
```
Invalid address error: ☐ PASS  ☐ FAIL
Error message: _______________________

Insufficient inventory error: ☐ PASS  ☐ FAIL
Error message: _______________________

Error codes clear: ☐ YES  ☐ NO
Manual review possible: ☐ YES  ☐ NO
```

### Sample Error Messages:
```




```

### Notes:
```


```

---

## Acceptance Criterion 6: Inventory Sync

**Requirement:** Inventory sync prevents overselling across channels

### Test Steps:
1. [ ] Set test SKU to 0 fulfillable quantity in Amazon FBA
2. [ ] Create TikTok order with that SKU
3. [ ] Run order routing with inventory sync enabled
4. [ ] Verify order is blocked

### Expected Results:
- [ ] Order routing blocked with INSUFFICIENT_INVENTORY error
- [ ] Error message includes SKU and current inventory level
- [ ] Low stock warning generated for SKUs < threshold
- [ ] Inventory cache working (subsequent checks are fast)
- [ ] Cache TTL respected (5 minutes default)

### Actual Results:
```
Zero inventory SKU: ______________
Order blocked: ☐ YES  ☐ NO
Error message: ___________________
Low stock warnings: ☐ PASS  ☐ FAIL
Cache working: ☐ YES  ☐ NO
Status: ☐ PASS  ☐ FAIL
```

### Low Stock SKUs Found:
```
SKU: ______________ Quantity: ______
SKU: ______________ Quantity: ______
SKU: ______________ Quantity: ______
```

### Notes:
```


```

---

## Additional Verification

### Performance
- [ ] Order routing completes in < 30 seconds per order
- [ ] Batch processing uses concurrency (max 5 concurrent by default)
- [ ] API rate limits respected (no 429 errors)
- [ ] Memory usage reasonable for large batches (< 512 MB)

### Security
- [ ] No secrets in source code (grep check)
- [ ] All credentials loaded from environment variables
- [ ] Sensitive data not logged to console
- [ ] HTTPS used for all API calls
- [ ] Tokens refreshed automatically when expired

### Error Recovery
- [ ] Transient errors retried with exponential backoff
- [ ] Non-retryable errors fail immediately
- [ ] Batch processing continues on individual failures
- [ ] Failed orders logged for manual review
- [ ] Retry count configurable

### Monitoring
- [ ] Connection test method works
- [ ] Statistics methods return accurate data
- [ ] Scheduler status queryable
- [ ] Low stock alerts functional

---

## Test Execution Log

### Automated Tests
```bash
$ npm run test:e2e

Test Suites: __ passed, __ total
Tests:       __ passed, __ total
Time:        _______ s
```

### Manual Verification
```bash
$ tsx scripts/verify-e2e.ts --step=full

Results:
  Orders Detected: _______
  Orders Routed: _______
  Tracking Synced: _______
  Status: ☐ PASS  ☐ FAIL
```

---

## Overall Assessment

### All Acceptance Criteria Met
- [ ] Criterion 1: Order detection < 5 minutes
- [ ] Criterion 2: Order validation and transformation
- [ ] Criterion 3: MCF order creation with correct mapping
- [ ] Criterion 4: Tracking sync < 4 hours
- [ ] Criterion 5: Failed order handling
- [ ] Criterion 6: Inventory sync prevents overselling

### Ready for Production
- [ ] All acceptance criteria passed
- [ ] Performance acceptable
- [ ] Security verified
- [ ] Error handling comprehensive
- [ ] Documentation complete

### Deployment Approval
- [ ] ☐ APPROVED for staging deployment
- [ ] ☐ APPROVED for production deployment
- [ ] ☐ NOT APPROVED - see blockers below

### Blockers (if any)
```




```

### Recommendations
```




```

---

## Sign-off

**QA Tester:** ______________________  **Date:** __________

**Tech Lead:** ______________________  **Date:** __________

**Product Owner:** __________________  **Date:** __________

---

## Appendix: Test Data

### Test Order IDs Created
```
1. _______________________
2. _______________________
3. _______________________
```

### Test SKUs Used
```
1. _______________________
2. _______________________
3. _______________________
```

### Environment Configuration Used
```
TIKTOK_SHOP_ID: _________________
AMAZON_SELLER_ID: _______________
AMAZON_MARKETPLACE_ID: __________
AMAZON_REGION: __________________
```

### Screenshots/Evidence
```
Attach screenshots or links to evidence:
1. TikTok order creation: _______________
2. MCF order in Amazon: ________________
3. Tracking sync in TikTok: ____________
4. Error handling examples: ____________
```
