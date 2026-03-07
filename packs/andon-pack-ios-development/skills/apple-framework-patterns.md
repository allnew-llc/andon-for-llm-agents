---
name: apple-framework-patterns
description: Common Apple framework API patterns and troubleshooting.
---

# Apple Framework Patterns

## SwiftUI Common Issues

### View Not Updating

| Symptom | Cause | Fix |
|---------|-------|-----|
| View doesn't refresh | Property not `@State`/`@Binding` | Use appropriate property wrapper |
| List not updating | Array identity not tracked | Add `.id()` or use `Identifiable` |
| Sheet not dismissing | Missing `@Environment(\.dismiss)` | Add dismiss environment value |
| Navigation broken | `NavigationStack` vs legacy `NavigationView` | Migrate to `NavigationStack` |

### Property Wrappers

```swift
@State           // View-local mutable state
@Binding         // Two-way connection to parent's state
@StateObject     // Owned ObservableObject (create here)
@ObservedObject  // Borrowed ObservableObject (passed in)
@EnvironmentObject // Injected via .environmentObject()
@Observable      // Swift 5.9+ macro (replaces ObservableObject)
```

## HealthKit Quick Start

```swift
import HealthKit

let store = HKHealthStore()

// Check availability
guard HKHealthStore.isHealthDataAvailable() else { return }

// Request authorization
let types: Set<HKSampleType> = [
    HKQuantityType(.stepCount),
    HKQuantityType(.bodyMass),
]
try await store.requestAuthorization(toShare: [], read: types)

// Query
let descriptor = HKSampleQueryDescriptor(
    predicates: [.quantitySample(type: .init(.stepCount))],
    sortDescriptors: [SortDescriptor(\.startDate, order: .reverse)],
    limit: 10
)
let results = try await descriptor.result(for: store)
```

**Required**: Add `NSHealthShareUsageDescription` to Info.plist.

## Camera / AVFoundation

```swift
import AVFoundation

// Check permission
switch AVCaptureDevice.authorizationStatus(for: .video) {
case .authorized: break
case .notDetermined:
    await AVCaptureDevice.requestAccess(for: .video)
case .denied, .restricted:
    // Direct user to Settings
@unknown default: break
}
```

**Required**: Add `NSCameraUsageDescription` to Info.plist.

## Speech Recognition

```swift
import Speech

let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "ja-JP"))
try await SFSpeechRecognizer.requestAuthorization()
```

**Required**: Add `NSSpeechRecognitionUsageDescription` to Info.plist.

## Common Build Error Fixes

| Error | Fix |
|-------|-----|
| `No such module 'X'` | Add framework in Build Phases → Link Binary |
| `PRODUCT_MODULE_NAME` conflict | Rename target to avoid Swift keyword collision |
| `Undefined symbol` | Check target membership of source files |
| `Sandbox: deny` | Add entitlements or capabilities |
| `dyld: Library not loaded` | Embed framework (Embed & Sign) |

## Concurrency Patterns (Swift 6)

```swift
// Actor isolation
@MainActor
class ViewModel: ObservableObject {
    @Published var items: [Item] = []

    func load() async {
        let data = await fetchFromNetwork()  // runs off main
        items = data  // updates on main (actor-isolated)
    }
}

// Task cancellation
let task = Task {
    try await longRunningWork()
}
task.cancel()  // cooperative cancellation
```
