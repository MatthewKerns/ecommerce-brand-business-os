# Build Button Fix for Roadmap Features

## Issue
The new features (32-41) added to the roadmap were not showing the "Build" button in the Auto-Claude UI.

## Root Cause
The Auto-Claude frontend (FeatureCard component) displays:
- **"Build" button**: When a feature has NO `linked_spec_id` or it's null/undefined
- **"Go to Task" button**: When a feature HAS a `linked_spec_id` value

The new features were mistakenly added with `linked_spec_id` values (e.g., "032-blog-content-creation-ui"), which made the system think they already had specifications created.

## Solution Applied
Removed the `linked_spec_id` field from all new features (32-41) in the roadmap.json file.

## Features Fixed
- feature-32: Blog Content Creation UI
- feature-33: Social Media Content Pipeline
- feature-34: TikTok Video Generation & Publishing
- feature-35: Real-Time Analytics Dashboard
- feature-36: Content Performance Tracking
- feature-37: Email Sequence Builder
- feature-38: Cart Recovery Automation UI
- feature-39: Workflow Automation Builder
- feature-40: Brand Guide Upload & Processing
- feature-41: Onboarding Wizard

## How the Build Button Works
1. When you click "Build" on a feature, Auto-Claude:
   - Calls `onConvertToSpec(feature)`
   - Creates a specification file
   - Updates the feature with a `linked_spec_id`
   - Changes button from "Build" to "Go to Task"

2. Features must have:
   - `status` !== 'done' (ours are all 'planned' ✓)
   - No `linked_spec_id` field (now fixed ✓)

## Verification
All features 32-41 now:
- Have valid JSON structure
- Have NO `linked_spec_id` field
- Should display the "Build" button in the UI

## Next Steps
1. Refresh the Auto-Claude UI
2. Navigate to the Roadmap view
3. Features 32-41 should now show "Build" buttons
4. Click "Build" on any feature to generate its specification