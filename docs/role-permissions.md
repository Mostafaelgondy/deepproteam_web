Defining a **Role-Based Access Control (RBAC)** system is essential for **Deepproteam** to ensure that dealers don't access admin settings and clients don't access dealer sales data.

Here is the professional `docs/role-permissions.md` file. It maps user roles to specific capabilities and UI access levels.

---

# 🔐 Role & Permissions Matrix

This document outlines the access levels for the three primary user roles within the Deepproteam ecosystem.

## 1. Role Definitions

| Role | Description | Primary Interface |
| --- | --- | --- |
| **Client** | End-users who browse and purchase digital assets. | `/client/` (Shop) |
| **Dealer** | Vendors who publish products and manage their own sales. | `/dealer/` (Portal) |
| **Admin** | System overseers who manage users, disputes, and site settings. | `/admin/` (Dashboard) |

---

## 2. Permission Mapping

The following table defines which actions each role is authorized to perform.

| Feature | Action | Client | Dealer | Admin |
| --- | --- | --- | --- | --- |
| **Marketplace** | Browse & Search Products | ✅ | ✅ | ✅ |
|  | Purchase Products | ✅ | ❌ | ❌ |
|  | Rate/Review Products | ✅ | ❌ | ❌ |
| **Product Mgmt** | Create/Edit Own Products | ❌ | ✅ | ✅ |
|  | Delete/Archive Own Products | ❌ | ✅ | ✅ |
|  | Global Product Moderation | ❌ | ❌ | ✅ |
| **Order Mgmt** | View Personal Purchase History | ✅ | ❌ | ❌ |
|  | View Own Sales Analytics | ❌ | ✅ | ✅ |
|  | Issue Refunds/Manage Disputes | ❌ | ⚠️ | ✅ |
| **Financials** | Manage Billing/Subscription | ❌ | ✅ | ✅ |
|  | Set Global Commission Rates | ❌ | ❌ | ✅ |
| **User Mgmt** | Ban/Suspend Users | ❌ | ❌ | ✅ |
|  | Verify Dealer Identity | ❌ | ❌ | ✅ |

> **Note:** ⚠️ (Dealer Refund Permission) is restricted to specific timeframes or requires Admin oversight depending on the "Enterprise" vs "Starter" plan.

---

## 3. UI Access Control (Frontend Logic)

The frontend uses the `CONFIG.STORAGE.USER_DATA` to determine which sidebar links and pages to render.

### Route Guard Implementation

When a user attempts to access a protected directory, the `auth.service.js` performs a check:

```javascript
// Example Guard Logic
const checkAccess = (requiredRole) => {
    const user = UTILS.storageGet(CONFIG.STORAGE.USER_DATA);
    if (!user || user.role !== requiredRole) {
        window.location.href = CONFIG.PATHS.LOGIN;
    }
};

```

### Plan-Based Feature Locking (Dealers Only)

Within the Dealer role, certain UI elements are further restricted by the **Subscription Plan**:

* **Starter:** Maximum 5 active products.
* **Professional:** Access to "Priority Support" button.
* **Enterprise:** Access to "Custom Analytics" tab and lower commission badges.

---

### Next Step for the Project

To make these roles "real" in your code, would you like me to create the **`assets/js/core/auth-guard.js`**? This script will sit at the top of your HTML files and automatically redirect users if they try to access a page their role doesn't permit.