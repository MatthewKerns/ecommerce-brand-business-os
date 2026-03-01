# MCF Connector - Order Routing Engine

Build the core connector that automatically routes TikTok Shop orders to Amazon MCF for fulfillment. Includes order validation, address normalization, inventory checking, and fulfillment status sync back to TikTok.

## Rationale
This is the unique technical integration that no competitor offers. Directly addresses competitor pain-6-1 (TikTok FBT logistics chaos causing six-figure losses) and pain-6-2 (severe delivery delays). Transforms a critical weakness of TikTok Shop into a strength.

## User Stories
- As a brand owner, I want TikTok orders fulfilled through Amazon so that I have reliable delivery without FBT problems
- As a customer, I want consistent fast shipping regardless of where I purchased so that I trust the brand

## Acceptance Criteria
- [ ] New TikTok Shop orders automatically detected within 5 minutes
- [ ] Order data validated and transformed for MCF requirements
- [ ] MCF fulfillment orders created with correct product mapping
- [ ] Tracking numbers synced back to TikTok Shop within 4 hours of shipment
- [ ] Failed orders flagged for manual review with clear error messages
- [ ] Inventory sync prevents overselling across channels
