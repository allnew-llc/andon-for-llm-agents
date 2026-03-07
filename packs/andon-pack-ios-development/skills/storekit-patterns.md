---
name: storekit-patterns
description: StoreKit 2 implementation patterns for in-app purchases and subscriptions.
---

# StoreKit 2 Patterns

## Product Configuration

### App Store Connect Setup

1. App → In-App Purchases → Create
2. Choose type: Consumable, Non-Consumable, Auto-Renewable Subscription
3. Set Reference Name, Product ID, Price
4. For subscriptions: create Subscription Group first

### Product IDs Convention

```
com.yourcompany.appname.product_type
com.yourcompany.appname.premium_monthly
com.yourcompany.appname.premium_yearly
com.yourcompany.appname.coins_100
```

## Basic Implementation

### Loading Products

```swift
import StoreKit

let productIDs = ["com.example.premium_monthly", "com.example.premium_yearly"]
let products = try await Product.products(for: productIDs)

for product in products {
    print("\(product.displayName): \(product.displayPrice)")
}
```

### Making a Purchase

```swift
let result = try await product.purchase()

switch result {
case .success(let verification):
    let transaction = try checkVerified(verification)
    // Deliver content
    await transaction.finish()

case .userCancelled:
    break

case .pending:
    // Awaiting approval (Ask to Buy, etc.)
    break

@unknown default:
    break
}

func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
    switch result {
    case .unverified: throw StoreError.verificationFailed
    case .verified(let value): return value
    }
}
```

### Transaction Listener

Start early in app lifecycle (e.g., `App.init()`):

```swift
func listenForTransactions() -> Task<Void, Error> {
    Task.detached {
        for await result in Transaction.updates {
            guard let transaction = try? result.payloadValue else { continue }
            // Update entitlements
            await transaction.finish()
        }
    }
}
```

### Checking Entitlements

```swift
func isPremium() async -> Bool {
    for await result in Transaction.currentEntitlements {
        if let transaction = try? result.payloadValue,
           transaction.productID == "com.example.premium_monthly" {
            return true
        }
    }
    return false
}
```

### Restore Purchases

```swift
// StoreKit 2 handles this automatically via Transaction.currentEntitlements
// But add a button for user confidence:
try await AppStore.sync()
```

## Subscription Management

```swift
// Show subscription management
if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene {
    try await AppStore.showManageSubscriptions(in: windowScene)
}
```

## Testing

### StoreKit Configuration File

1. File → New → StoreKit Configuration File
2. Add products matching your App Store Connect setup
3. Scheme → Edit Scheme → Options → StoreKit Configuration

### StoreKit Testing in Xcode

```swift
// In tests
let session = try SKTestSession(configurationFileNamed: "Products")
session.disableDialogs = true
session.clearTransactions()
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Product not found" | Product ID mismatch or not approved | Check ASC product status |
| "Purchase not allowed" | Device restrictions | Test on real device with sandbox account |
| "Receipt validation failed" | Using StoreKit 1 receipt with StoreKit 2 | Use `Transaction` API instead |
| Sandbox purchase loops | Sandbox environment issue | Sign out, sign in with fresh sandbox account |

## App Store Review Compliance

- [ ] Restore Purchases button visible and functional
- [ ] Subscription terms displayed before purchase
- [ ] Cancel/manage subscription link provided
- [ ] Free trial duration clearly shown
- [ ] Price displayed in user's locale (StoreKit handles this)
