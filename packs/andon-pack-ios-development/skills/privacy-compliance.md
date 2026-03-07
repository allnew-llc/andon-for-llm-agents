---
name: privacy-compliance
description: Privacy manifest and data collection compliance for iOS apps.
---

# iOS Privacy Compliance Guide

## Privacy Manifest (PrivacyInfo.xcprivacy)

Required since Spring 2024.  Must declare:

1. **Required Reason APIs** used by your app and SDKs
2. **Tracking domains** (if any)
3. **Data collection** types
4. **Tracking** declaration

### Required Reason APIs

| API Category | Common APIs | Requires Reason |
|-------------|-------------|-----------------|
| File timestamp | `NSFileCreationDate`, `NSFileModificationDate` | Yes |
| System boot time | `systemUptime`, `mach_absolute_time` | Yes |
| Disk space | `volumeAvailableCapacity` | Yes |
| User defaults | `UserDefaults` (when accessed by SDKs) | Yes |
| Active keyboards | `activeInputModes` | Yes |

### Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSPrivacyTracking</key>
    <false/>
    <key>NSPrivacyTrackingDomains</key>
    <array/>
    <key>NSPrivacyCollectedDataTypes</key>
    <array>
        <!-- Add collected data types here -->
    </array>
    <key>NSPrivacyAccessedAPITypes</key>
    <array>
        <dict>
            <key>NSPrivacyAccessedAPIType</key>
            <string>NSPrivacyAccessedAPICategoryUserDefaults</string>
            <key>NSPrivacyAccessedAPITypeReasons</key>
            <array>
                <string>CA92.1</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
```

## Privacy Nutrition Labels

Configure in App Store Connect under App Privacy.

### Data Types

| Category | Examples | When to Declare |
|----------|---------|-----------------|
| Contact Info | Name, email, phone | User registration |
| Health & Fitness | Steps, weight, heart rate | HealthKit usage |
| Financial Info | Payment info | IAP (handled by Apple) |
| Location | Precise/coarse location | Location services |
| Usage Data | Product interaction | Analytics |
| Diagnostics | Crash data, performance | Crash reporting SDKs |

### Data Use Purposes

- App Functionality
- Analytics
- Product Personalization
- Third-Party Advertising
- Developer's Advertising or Marketing

### Linked vs. Not Linked to Identity

| Linked | Not Linked |
|--------|------------|
| User account + data | Anonymous analytics |
| Personalized content | Aggregated crash reports |
| User preferences with login | Device-only preferences |

## App Tracking Transparency (ATT)

Required if you track users across apps/websites owned by others.

```swift
import AppTrackingTransparency

let status = await ATTrackingManager.requestTrackingAuthorization()
switch status {
case .authorized: // Enable tracking
case .denied, .restricted: // Disable tracking
case .notDetermined: break
@unknown default: break
}
```

**Required**: Add `NSUserTrackingUsageDescription` to Info.plist.

## Common ITMS Errors

| Error Code | Issue | Fix |
|-----------|-------|-----|
| ITMS-91053 | Missing privacy manifest | Add PrivacyInfo.xcprivacy |
| ITMS-91056 | Missing Required Reason API declaration | Declare API reasons |
| ITMS-90683 | Missing purpose string | Add NS*UsageDescription |

## Third-Party SDK Audit

Check each SDK for:
- [ ] Includes its own PrivacyInfo.xcprivacy
- [ ] Data collection disclosed in documentation
- [ ] Tracking domains listed (if applicable)
- [ ] Updated to latest version with privacy manifest
