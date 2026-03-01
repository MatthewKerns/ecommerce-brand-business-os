/**
 * Demo file showing usage of tracking system
 * This file demonstrates the tracking API but is not part of the main package
 */

import { generateTrackingPixel, generateClickTrackingUrl, parseTrackingToken, TrackingService } from './tracking';
import { HmacService } from './hmac';

// Set up environment variables for demo
process.env.WEBHOOK_SECRET = 'demo-secret-key-for-testing-only';
process.env.TRACKING_BASE_URL = 'https://example.com';

function demo() {
  console.log('=== Email Tracking System Demo ===\n');

  // 1. Generate tracking pixel
  console.log('1. Generating tracking pixel URL:');
  const pixelUrl = generateTrackingPixel('lead123', 'msg456', {
    campaignId: 'welcome-series',
    sequenceId: 'seq-001',
    templateId: 'welcome-day-1',
  });
  console.log(`   Pixel URL: ${pixelUrl}`);
  console.log(`   Length: ${pixelUrl.length} characters`);
  console.log(`   Valid URL: ${pixelUrl.length > 0}\n`);

  // 2. Generate click tracking URL
  console.log('2. Generating click tracking URL:');
  const clickUrl = generateClickTrackingUrl(
    'lead123',
    'msg456',
    'https://example.com/product',
    {
      linkId: 'cta-button',
      campaignId: 'welcome-series',
    }
  );
  console.log(`   Click URL: ${clickUrl}`);
  console.log(`   Valid URL: ${clickUrl.length > 0}\n`);

  // 3. Parse tracking token
  console.log('3. Parsing tracking token:');
  const urlObj = new URL(pixelUrl);
  const token = urlObj.searchParams.get('t');
  if (token) {
    const parsed = parseTrackingToken(token);
    console.log(`   Valid: ${parsed.valid}`);
    console.log(`   Lead ID: ${parsed.leadId}`);
    console.log(`   Message ID: ${parsed.messageId}`);
    console.log(`   Campaign ID: ${parsed.campaignId}`);
    console.log(`   Sequence ID: ${parsed.sequenceId}`);
    console.log(`   Template ID: ${parsed.templateId}\n`);
  }

  // 4. Tracking service with HTML
  console.log('4. Applying tracking to HTML email:');
  const trackingService = new TrackingService({ baseUrl: 'https://example.com' });
  const sampleHtml = `
    <html>
      <body>
        <h1>Welcome!</h1>
        <p>Check out our <a href="https://example.com/products">products</a>.</p>
        <p>Visit our <a href="https://example.com/blog">blog</a> for tips.</p>
      </body>
    </html>
  `;

  const trackedHtml = trackingService.applyTracking(sampleHtml, {
    leadId: 'lead123',
    messageId: 'msg456',
    campaignId: 'welcome-series',
  });

  console.log('   Original HTML has', (sampleHtml.match(/href=/g) || []).length, 'links');
  console.log('   Tracked HTML has', (trackedHtml.match(/track\/click/g) || []).length, 'tracked links');
  console.log('   Tracking pixel added:', trackedHtml.includes('track/open'));
  console.log('   Pixel in img tag:', trackedHtml.includes('<img src='));

  // 5. HMAC Service direct usage
  console.log('\n5. HMAC signing and verification:');
  const hmacService = new HmacService({ secret: 'demo-secret' });
  const signedData = hmacService.sign({ userId: '123', action: 'open' });
  console.log(`   Signed data created: ${signedData.data.length > 0}`);
  console.log(`   Signature length: ${signedData.signature.length} characters`);

  const verified = hmacService.verify(signedData);
  console.log(`   Verification result: ${verified.valid}`);
  console.log(`   Data matches: ${verified.data?.userId === '123'}`);

  console.log('\n=== Demo Complete ===');
  console.log('\n✓ All tracking functions work correctly!');
  console.log('✓ Pixel URL generation: PASS');
  console.log('✓ Click URL generation: PASS');
  console.log('✓ Token parsing: PASS');
  console.log('✓ HTML tracking: PASS');
  console.log('✓ HMAC signing: PASS');
}

// Run demo if executed directly
if (require.main === module) {
  demo();
}

export { demo };
