---
name: app-review-guide
description: App Store Review Guidelines quick reference for common rejection reasons.
---

# App Store Review Guidelines Reference

## Most Common Rejection Reasons

### Guideline 2.1 — App Completeness

- App crashes or has obvious bugs
- Placeholder content or lorem ipsum text
- Missing functionality described in metadata

**Fix**: Test all flows on device before submission.

### Guideline 2.3 — Accurate Metadata

| Issue | Example | Fix |
|-------|---------|-----|
| Misleading screenshots | Screenshots show features not in app | Update screenshots |
| Wrong category | Health app in Utilities | Change category |
| Keyword stuffing | Competitor names in keywords | Remove irrelevant terms |

### Guideline 3.1.1 — In-App Purchase

- All digital content/features must use IAP
- Physical goods/services can use external payment
- "Reader" apps have specific rules

**Fix**: Use StoreKit for digital goods. Link to subscription management.

### Guideline 4.0 — Design (Minimum Functionality)

- App is too simple (single webpage wrapper)
- No meaningful functionality beyond website
- Template app without customization

### Guideline 5.1.1 — Data Collection and Storage

- Missing privacy policy
- Collecting data without disclosure
- Required Reason API usage without declaration

**Fix**: Add privacy policy URL, complete Privacy Nutrition Labels,
add PrivacyInfo.xcprivacy.

### Guideline 5.1.2 — Data Use and Sharing

- Sharing data with third parties without disclosure
- SDK data collection not declared
- Tracking without ATT prompt

## Pre-Submission Checklist

### Required Items

- [ ] Privacy Policy URL (displayed in app + ASC)
- [ ] Support URL
- [ ] App category selected
- [ ] Age rating questionnaire completed
- [ ] Screenshots for all required device sizes
- [ ] App description (no placeholder text)
- [ ] PrivacyInfo.xcprivacy included in bundle

### If Using HealthKit

- [ ] HealthKit entitlement enabled
- [ ] `NSHealthShareUsageDescription` in Info.plist
- [ ] App review notes explain HealthKit usage
- [ ] Human readable purpose strings for each data type

### If Using IAP/Subscriptions

- [ ] Products configured in ASC
- [ ] Subscription group created (if applicable)
- [ ] Restore Purchases button accessible
- [ ] Subscription management link provided
- [ ] Terms clearly displayed before purchase

### If Using Location

- [ ] `NSLocationWhenInUseUsageDescription` set
- [ ] Location usage explained in review notes
- [ ] Privacy Nutrition Label declares location data

## Appeal Process

If rejected unfairly:
1. Reply to the Resolution Center message with evidence
2. Reference specific guideline sections
3. Include screenshots/video of the disputed feature
4. If no resolution, request an appeal via the App Review Board
