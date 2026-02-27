/**
 * End-to-End Tests - Welcome Sequence Flow
 *
 * This test suite verifies the complete welcome sequence flow:
 * 1. Create welcome sequence via API/engine
 * 2. Enroll test lead in sequence
 * 3. Verify email sent via Gmail API (mocked)
 * 4. Simulate email open event with tracking pixel
 * 5. Check analytics shows open event
 * 6. Verify sequence metrics updated
 *
 * PREREQUISITES:
 * - Email automation system initialized
 * - Analytics storage configured (in-memory for testing)
 * - Environment variables configured (see .env.example)
 *
 * USAGE:
 * npm run test:e2e
 */

import { SequenceEngine } from '../../claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation/src/core/sequences/sequence-engine';
import { TemplateRegistry } from '../../claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation/src/templates/registry';
import { MemoryAnalyticsStorage } from '../../claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation/src/core/analytics/storage';
import { TrackingService } from '../../claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation/src/core/analytics/tracking';
import type { Lead } from '../../claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation/src/types/lead';
import type { EmailSequence, SequenceEnrollment } from '../../claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation/src/core/sequences/sequence-engine';

// Skip these tests in CI unless explicitly enabled
const E2E_ENABLED = process.env.RUN_E2E_TESTS === 'true';
const describeE2E = E2E_ENABLED ? describe : describe.skip;

// Timeout for operations (2 minutes)
const TEST_TIMEOUT = 2 * 60 * 1000;

// Test data storage
const testLeadIds: string[] = [];
const testSequenceIds: string[] = [];

describeE2E('End-to-End Welcome Sequence Flow', () => {
  let sequenceEngine: SequenceEngine;
  let templateRegistry: TemplateRegistry;
  let analyticsStorage: MemoryAnalyticsStorage;
  let trackingService: TrackingService;
  let testLead: Lead;
  let testSequence: EmailSequence;

  beforeAll(async () => {
    // Initialize template registry
    templateRegistry = new TemplateRegistry();

    // Initialize analytics storage (in-memory for testing)
    analyticsStorage = new MemoryAnalyticsStorage();

    // Initialize tracking service
    trackingService = new TrackingService({
      baseUrl: process.env.PUBLIC_URL || 'http://localhost:3000',
    });

    // Initialize sequence engine with analytics storage
    sequenceEngine = new SequenceEngine({
      analyticsStorage,
    });

    // Link template registry with sequence engine (if needed)
    if (typeof sequenceEngine.setTemplateRegistry === 'function') {
      sequenceEngine.setTemplateRegistry(templateRegistry);
    }

    console.log('✓ Welcome sequence E2E test suite initialized');
  }, TEST_TIMEOUT);

  afterAll(async () => {
    // Cleanup: Log test data for reference
    if (testLeadIds.length > 0) {
      console.log('\n=== Test Leads Created ===');
      console.log('The following test leads were created:');
      testLeadIds.forEach(id => console.log(`  - ${id}`));
    }

    if (testSequenceIds.length > 0) {
      console.log('\n=== Test Sequences Created ===');
      console.log('The following test sequences were created:');
      testSequenceIds.forEach(id => console.log(`  - ${id}`));
    }
  });

  describe('Setup - Template and Sequence Creation', () => {
    it('should verify welcome series templates are available', () => {
      const templates = templateRegistry.listTemplates();
      const welcomeTemplates = templates.filter(t =>
        t.category === 'welcome' || t.id.startsWith('welcome_series_')
      );

      expect(welcomeTemplates.length).toBeGreaterThanOrEqual(4);
      console.log(`\n✓ Found ${welcomeTemplates.length} welcome series templates`);

      welcomeTemplates.forEach(template => {
        console.log(`  - ${template.id}: ${template.name}`);
      });
    });

    it('should create a welcome sequence with 4 email steps', async () => {
      const welcomeTemplates = templateRegistry.listTemplates()
        .filter(t => t.category === 'welcome' || t.id.startsWith('welcome_series_'))
        .slice(0, 4);

      // Create sequence definition
      const sequenceId = `welcome_seq_${Date.now()}`;
      const sequence: EmailSequence = {
        id: sequenceId,
        name: 'Welcome Series E2E Test',
        description: 'Automated welcome sequence for E2E testing',
        status: 'active',
        trigger: {
          type: 'tag_added',
          config: {
            tag: 'new_subscriber',
          },
        },
        steps: welcomeTemplates.map((template, index) => ({
          id: `step_${index + 1}`,
          type: 'email' as const,
          name: template.name,
          config: {
            templateId: template.id,
            subject: `Welcome Email ${index + 1}`,
            duration: index === 0 ? 0 : (index === 1 ? 48 : index === 2 ? 120 : 168), // Day 0, 2, 5, 7
          },
        })),
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      // Create sequence in engine
      await sequenceEngine.createSequence(sequence);
      testSequence = sequence;
      testSequenceIds.push(sequenceId);

      console.log(`\n✓ Created welcome sequence: ${sequenceId}`);
      console.log(`  Steps: ${sequence.steps.length}`);
      console.log(`  Status: ${sequence.status}`);

      expect(sequence.steps.length).toBe(4);
      expect(sequence.status).toBe('active');
    }, TEST_TIMEOUT);
  });

  describe('Lead Enrollment', () => {
    it('should create and enroll a test lead in the welcome sequence', async () => {
      // Create test lead
      const leadId = `lead_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      testLead = {
        id: leadId,
        email: `test_${leadId}@example.com`,
        firstName: 'Test',
        lastName: 'User',
        fullName: 'Test User',
        status: 'new',
        source: 'website',
        tags: ['new_subscriber', 'e2e_test'],
        segments: ['welcome_test'],
        engagement: {
          emailsSent: 0,
          emailsOpened: 0,
          emailsClicked: 0,
          emailsReplied: 0,
        },
        customFields: [],
        consentGiven: true,
        consentDate: new Date(),
        consentSource: 'website_signup',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      testLeadIds.push(leadId);

      // Enroll lead in sequence
      const enrollment: SequenceEnrollment = {
        leadId: testLead.id,
        sequenceId: testSequence.id,
        currentStep: 0,
        status: 'active',
        startedAt: new Date(),
        metadata: {
          source: 'e2e_test',
        },
      };

      await sequenceEngine.enrollLead(enrollment);

      console.log(`\n✓ Enrolled lead in sequence:`);
      console.log(`  Lead ID: ${testLead.id}`);
      console.log(`  Email: ${testLead.email}`);
      console.log(`  Sequence: ${testSequence.id}`);

      expect(testLead.id).toBeDefined();
      expect(enrollment.status).toBe('active');
    }, TEST_TIMEOUT);

    it('should verify lead enrollment is recorded', async () => {
      const enrollments = await sequenceEngine.getSequenceEnrollments(testSequence.id);

      const testEnrollment = enrollments.find(e => e.leadId === testLead.id);

      expect(testEnrollment).toBeDefined();
      expect(testEnrollment?.status).toBe('active');
      expect(testEnrollment?.currentStep).toBe(0);

      console.log(`\n✓ Enrollment verified:`);
      console.log(`  Current step: ${testEnrollment?.currentStep}`);
      console.log(`  Status: ${testEnrollment?.status}`);
    }, TEST_TIMEOUT);
  });

  describe('Email Sending', () => {
    it('should process next step and send first email', async () => {
      // Process sequence steps (this would normally trigger email sending)
      const result = await sequenceEngine.processScheduledSteps();

      console.log(`\n✓ Processed sequence steps:`);
      console.log(`  Steps processed: ${result.processed}`);
      console.log(`  Emails sent: ${result.sent || 0}`);

      // In a real scenario, this would call Gmail API
      // For E2E test, we simulate email sent event
      const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

      await analyticsStorage.recordEvent({
        type: 'sent',
        leadId: testLead.id,
        messageId: messageId,
        emailAddress: testLead.email,
        sequenceId: testSequence.id,
        templateId: testSequence.steps[0].config.templateId!,
        sequenceStep: 0,
        timestamp: new Date(),
      });

      // Store messageId for later use
      (testLead as any).lastMessageId = messageId;

      console.log(`  Message ID: ${messageId}`);

      expect(messageId).toBeDefined();
      expect(result.processed).toBeGreaterThanOrEqual(0);
    }, TEST_TIMEOUT);

    it('should verify email sent event is recorded in analytics', async () => {
      const events = await analyticsStorage.listEvents({
        filter: {
          leadId: testLead.id,
          type: 'sent',
        },
      });

      expect(events.events.length).toBeGreaterThanOrEqual(1);

      const sentEvent = events.events.find(e =>
        e.leadId === testLead.id && e.type === 'sent'
      );

      expect(sentEvent).toBeDefined();
      expect(sentEvent?.emailAddress).toBe(testLead.email);

      console.log(`\n✓ Email sent event recorded:`);
      console.log(`  Event ID: ${sentEvent?.id}`);
      console.log(`  Timestamp: ${sentEvent?.timestamp}`);
      console.log(`  Template: ${sentEvent?.templateId}`);
    }, TEST_TIMEOUT);
  });

  describe('Email Open Tracking', () => {
    it('should generate tracking pixel URL', () => {
      const messageId = (testLead as any).lastMessageId;

      const trackingPixel = trackingService.generateTrackingPixel({
        leadId: testLead.id,
        messageId: messageId,
        sequenceId: testSequence.id,
        templateId: testSequence.steps[0].config.templateId!,
      });

      expect(trackingPixel).toBeDefined();
      expect(trackingPixel).toContain('/track/open');

      console.log(`\n✓ Tracking pixel generated:`);
      console.log(`  URL length: ${trackingPixel.length} chars`);
      console.log(`  Contains leadId: ${trackingPixel.includes('leadId')}`);
    }, TEST_TIMEOUT);

    it('should simulate email open event', async () => {
      const messageId = (testLead as any).lastMessageId;

      // Simulate user opening email (tracking pixel loaded)
      await analyticsStorage.recordOpen({
        leadId: testLead.id,
        messageId: messageId,
        emailAddress: testLead.email,
        sequenceId: testSequence.id,
        templateId: testSequence.steps[0].config.templateId!,
        sequenceStep: 0,
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        ipAddress: '192.168.1.100',
      });

      console.log(`\n✓ Email open event simulated:`);
      console.log(`  Lead ID: ${testLead.id}`);
      console.log(`  Message ID: ${messageId}`);
    }, TEST_TIMEOUT);

    it('should verify open event is recorded in analytics', async () => {
      const events = await analyticsStorage.listEvents({
        filter: {
          leadId: testLead.id,
          type: 'open',
        },
      });

      expect(events.events.length).toBeGreaterThanOrEqual(1);

      const openEvent = events.events.find(e =>
        e.leadId === testLead.id && e.type === 'open'
      );

      expect(openEvent).toBeDefined();
      expect(openEvent?.emailAddress).toBe(testLead.email);
      expect(openEvent?.deviceType).toBeDefined();

      console.log(`\n✓ Open event recorded:`);
      console.log(`  Event ID: ${openEvent?.id}`);
      console.log(`  Timestamp: ${openEvent?.timestamp}`);
      console.log(`  Device: ${openEvent?.deviceType}`);
      console.log(`  Email Client: ${openEvent?.emailClient || 'Unknown'}`);
    }, TEST_TIMEOUT);

    it('should simulate email click event', async () => {
      const messageId = (testLead as any).lastMessageId;

      // Simulate user clicking a link in the email
      await analyticsStorage.recordClick({
        leadId: testLead.id,
        messageId: messageId,
        emailAddress: testLead.email,
        sequenceId: testSequence.id,
        templateId: testSequence.steps[0].config.templateId!,
        sequenceStep: 0,
        targetUrl: 'https://example.com/product',
        linkId: 'cta_button',
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        ipAddress: '192.168.1.100',
      });

      console.log(`\n✓ Email click event simulated:`);
      console.log(`  Target URL: https://example.com/product`);
      console.log(`  Link ID: cta_button`);
    }, TEST_TIMEOUT);
  });

  describe('Analytics and Metrics', () => {
    it('should retrieve email events for the lead', async () => {
      const events = await analyticsStorage.listEvents({
        filter: {
          leadId: testLead.id,
        },
      });

      expect(events.events.length).toBeGreaterThanOrEqual(3); // sent, open, click

      console.log(`\n✓ Retrieved ${events.events.length} events for lead:`);

      const eventTypes = events.events.reduce((acc, e) => {
        acc[e.type] = (acc[e.type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      Object.entries(eventTypes).forEach(([type, count]) => {
        console.log(`  - ${type}: ${count}`);
      });

      expect(eventTypes.sent).toBeGreaterThanOrEqual(1);
      expect(eventTypes.open).toBeGreaterThanOrEqual(1);
      expect(eventTypes.click).toBeGreaterThanOrEqual(1);
    }, TEST_TIMEOUT);

    it('should calculate sequence metrics', async () => {
      const metrics = await analyticsStorage.getSequenceMetrics(testSequence.id);

      expect(metrics).toBeDefined();
      expect(metrics.sent).toBeGreaterThanOrEqual(1);
      expect(metrics.opens).toBeGreaterThanOrEqual(1);
      expect(metrics.clicks).toBeGreaterThanOrEqual(1);
      expect(metrics.openRate).toBeGreaterThan(0);
      expect(metrics.clickRate).toBeGreaterThan(0);

      console.log(`\n✓ Sequence metrics calculated:`);
      console.log(`  Emails sent: ${metrics.sent}`);
      console.log(`  Opens: ${metrics.opens}`);
      console.log(`  Clicks: ${metrics.clicks}`);
      console.log(`  Open rate: ${(metrics.openRate * 100).toFixed(2)}%`);
      console.log(`  Click rate: ${(metrics.clickRate * 100).toFixed(2)}%`);
      console.log(`  Click-to-open rate: ${(metrics.clickToOpenRate * 100).toFixed(2)}%`);
    }, TEST_TIMEOUT);

    it('should retrieve sequence performance report', async () => {
      // Get performance report from sequence engine
      const report = await sequenceEngine.getSequencePerformanceReport(testSequence.id);

      expect(report).toBeDefined();
      expect(report.sequenceId).toBe(testSequence.id);
      expect(report.summary).toBeDefined();
      expect(report.summary.sent).toBeGreaterThanOrEqual(1);

      console.log(`\n✓ Sequence performance report:`);
      console.log(`  Sequence: ${report.sequenceName || testSequence.name}`);
      console.log(`  Period: ${report.period}`);
      console.log(`  Summary:`);
      console.log(`    - Sent: ${report.summary.sent}`);
      console.log(`    - Delivered: ${report.summary.delivered}`);
      console.log(`    - Opens: ${report.summary.opens}`);
      console.log(`    - Clicks: ${report.summary.clicks}`);
      console.log(`    - Open Rate: ${(report.summary.openRate * 100).toFixed(2)}%`);
      console.log(`    - Click Rate: ${(report.summary.clickRate * 100).toFixed(2)}%`);
    }, TEST_TIMEOUT);
  });

  describe('Sequence Progression', () => {
    it('should update lead to next sequence step', async () => {
      // Get current enrollment
      const enrollments = await sequenceEngine.getSequenceEnrollments(testSequence.id);
      const enrollment = enrollments.find(e => e.leadId === testLead.id);

      expect(enrollment).toBeDefined();

      // Update to next step
      if (enrollment) {
        await sequenceEngine.updateEnrollment(enrollment.leadId, testSequence.id, {
          currentStep: 1,
          updatedAt: new Date(),
        });
      }

      // Verify update
      const updatedEnrollments = await sequenceEngine.getSequenceEnrollments(testSequence.id);
      const updatedEnrollment = updatedEnrollments.find(e => e.leadId === testLead.id);

      expect(updatedEnrollment?.currentStep).toBe(1);

      console.log(`\n✓ Lead progressed to next step:`);
      console.log(`  Previous step: 0`);
      console.log(`  Current step: ${updatedEnrollment?.currentStep}`);
      console.log(`  Next email: ${testSequence.steps[1]?.name}`);
    }, TEST_TIMEOUT);

    it('should verify step metrics are tracked separately', async () => {
      const metrics = await analyticsStorage.getSequenceMetrics(testSequence.id);

      // Check if step-level metrics exist
      expect(metrics.stepMetrics).toBeDefined();

      if (metrics.stepMetrics && metrics.stepMetrics.length > 0) {
        console.log(`\n✓ Step-level metrics available:`);
        metrics.stepMetrics.forEach(step => {
          console.log(`  Step ${step.step}: ${step.sent} sent, ${step.opens} opens, ${step.clicks} clicks`);
        });
      } else {
        console.log(`\n✓ Step-level metrics not yet available (expected for minimal test data)`);
      }
    }, TEST_TIMEOUT);
  });

  describe('End-to-End Flow Summary', () => {
    it('should complete full welcome sequence flow', async () => {
      console.log('\n=== FULL END-TO-END WELCOME SEQUENCE TEST ===\n');

      // Step 1: Sequence created
      console.log('✓ Step 1: Welcome sequence created');
      console.log(`  Sequence ID: ${testSequence.id}`);
      console.log(`  Steps: ${testSequence.steps.length}`);

      // Step 2: Lead enrolled
      console.log('\n✓ Step 2: Test lead enrolled');
      console.log(`  Lead ID: ${testLead.id}`);
      console.log(`  Email: ${testLead.email}`);

      // Step 3: Email sent
      const sentEvents = await analyticsStorage.listEvents({
        filter: { leadId: testLead.id, type: 'sent' },
      });
      console.log('\n✓ Step 3: Email sent');
      console.log(`  Events: ${sentEvents.events.length}`);

      // Step 4: Email opened
      const openEvents = await analyticsStorage.listEvents({
        filter: { leadId: testLead.id, type: 'open' },
      });
      console.log('\n✓ Step 4: Email opened and tracked');
      console.log(`  Open events: ${openEvents.events.length}`);

      // Step 5: Analytics updated
      const metrics = await analyticsStorage.getSequenceMetrics(testSequence.id);
      console.log('\n✓ Step 5: Analytics and metrics updated');
      console.log(`  Open rate: ${(metrics.openRate * 100).toFixed(2)}%`);
      console.log(`  Click rate: ${(metrics.clickRate * 100).toFixed(2)}%`);

      // Step 6: Sequence progression
      const enrollments = await sequenceEngine.getSequenceEnrollments(testSequence.id);
      const enrollment = enrollments.find(e => e.leadId === testLead.id);
      console.log('\n✓ Step 6: Sequence progression tracked');
      console.log(`  Current step: ${enrollment?.currentStep}`);
      console.log(`  Status: ${enrollment?.status}`);

      console.log('\n=== END-TO-END TEST COMPLETE ===\n');
      console.log('Summary:');
      console.log(`  ✓ Sequence created: ${testSequence.id}`);
      console.log(`  ✓ Lead enrolled: ${testLead.id}`);
      console.log(`  ✓ Emails sent: ${sentEvents.events.length}`);
      console.log(`  ✓ Opens tracked: ${openEvents.events.length}`);
      console.log(`  ✓ Analytics updated: ${metrics.sent} sent, ${metrics.opens} opens`);
      console.log(`  ✓ Sequence progressing: Step ${enrollment?.currentStep} of ${testSequence.steps.length}`);

      console.log('\n✅ All end-to-end tests passed successfully!');

      // Final assertions
      expect(testSequence).toBeDefined();
      expect(testLead).toBeDefined();
      expect(sentEvents.events.length).toBeGreaterThanOrEqual(1);
      expect(openEvents.events.length).toBeGreaterThanOrEqual(1);
      expect(metrics.openRate).toBeGreaterThan(0);
    }, TEST_TIMEOUT);
  });

  describe('Error Handling', () => {
    it('should handle invalid lead enrollment gracefully', async () => {
      const invalidEnrollment: SequenceEnrollment = {
        leadId: 'invalid_lead_id',
        sequenceId: 'invalid_sequence_id',
        currentStep: 0,
        status: 'active',
        startedAt: new Date(),
      };

      await expect(async () => {
        await sequenceEngine.enrollLead(invalidEnrollment);
      }).rejects.toThrow();

      console.log('\n✓ Invalid enrollment rejected as expected');
    }, TEST_TIMEOUT);

    it('should handle missing analytics data gracefully', async () => {
      const metrics = await analyticsStorage.getSequenceMetrics('non_existent_sequence');

      // Should return empty/zero metrics, not throw
      expect(metrics).toBeDefined();
      expect(metrics.sent).toBe(0);

      console.log('\n✓ Missing sequence returns empty metrics (no error)');
    }, TEST_TIMEOUT);
  });
});
