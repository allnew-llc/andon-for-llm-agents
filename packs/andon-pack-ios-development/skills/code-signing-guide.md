---
name: code-signing-guide
description: Code signing and provisioning profile troubleshooting.
---

# Code Signing Troubleshooting Guide

## Symptom → Cause → Fix

| Error Message | Cause | Fix |
|--------------|-------|-----|
| "No signing certificate" | Certificate expired/missing | Regenerate in Xcode → Settings → Accounts |
| "Provisioning profile doesn't include signing certificate" | Profile/cert mismatch | Regenerate profile in Developer Portal |
| "No provisioning profiles with a valid signing identity" | No matching profile | Enable Automatic Signing |
| "The certificate chain is invalid" | Intermediate cert missing | Install Apple WWDR certificate |
| "Code signature invalid" | Binary modified after signing | Clean build, re-sign |
| "ITMS-90035: Invalid Signature" | Wrong distribution cert | Use Distribution (not Development) cert |

## Automatic vs. Manual Signing

### Automatic Signing (Recommended)

```
Build Settings:
  CODE_SIGN_STYLE = Automatic
  DEVELOPMENT_TEAM = YOUR_TEAM_ID
```

Xcode manages certificates and profiles. Best for most projects.

### Manual Signing

```
Build Settings:
  CODE_SIGN_STYLE = Manual
  CODE_SIGN_IDENTITY = "Apple Distribution"
  PROVISIONING_PROFILE_SPECIFIER = "YourApp Distribution"
```

Use when: CI/CD, multiple teams, specific entitlements.

## Entitlements

Common entitlements that need configuration:

| Entitlement | Capability | File Key |
|-------------|-----------|----------|
| HealthKit | Health data access | `com.apple.developer.healthkit` |
| iCloud | CloudKit / documents | `com.apple.developer.icloud-container-identifiers` |
| Push Notifications | APNs | `aps-environment` |
| App Groups | Shared container | `com.apple.security.application-groups` |
| Sign in with Apple | Apple ID auth | `com.apple.developer.applesignin` |

### Adding Entitlements

1. Xcode → Target → Signing & Capabilities → + Capability
2. Enable in Developer Portal → Identifiers → App ID
3. Regenerate provisioning profiles if manual signing

## CI/CD Code Signing

### Export for App Store

```bash
# Archive
xcodebuild archive \
  -project YourApp.xcodeproj \
  -scheme YourApp \
  -archivePath build/YourApp.xcarchive

# Export
xcodebuild -exportArchive \
  -archivePath build/YourApp.xcarchive \
  -exportPath build/export \
  -exportOptionsPlist ExportOptions.plist
```

### ExportOptions.plist

```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store-connect</string>
    <key>teamID</key>
    <string>YOUR_TEAM_ID</string>
    <key>signingStyle</key>
    <string>automatic</string>
</dict>
</plist>
```

## Common Fixes

### Reset Signing

1. Xcode → Settings → Accounts → Manage Certificates
2. Delete expired certificates
3. Click "+" to create new certificate
4. Clean Build Folder (Shift+Cmd+K)
5. Build again

### Profile Regeneration

1. Developer Portal → Profiles
2. Delete old profiles
3. Create new profile with correct cert + App ID
4. Download and double-click to install
