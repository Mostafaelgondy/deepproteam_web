This document maps the user journey and technical flow of the **Deepproteam** frontend. It serves as a blueprint for how the various components (Modals, Tables, Services) interact during a user session.

---

# 🌊 Frontend Application Flow

This document details the navigation logic, state management, and data lifecycle of the Deepproteam web application.

## 1. Authentication & Bootstrapping

Before any page content is interactive, the `core/app.js` and `core/auth-guard.js` execute the following lifecycle:

1. **Token Check**: The app checks `localStorage` for a valid `dpt_auth_token`.
2. **Role Verification**: If a token exists, the app compares the user's role against the current URL path (e.g., `/dealer/*` requires the `DEALER` role).
3. **Redirection**:
* No Token + Protected Path ➔ Redirect to `/login.html`.
* Wrong Role ➔ Redirect to assigned dashboard.
* Valid Token ➔ Initialize UI components.



---

## 2. Data Fetching & Rendering Pattern

We use a **Service-Component-Template** pattern to keep the code clean and maintainable.

### The Lifecycle of a Data-Driven Component (e.g., Product Grid):

1. **Trigger**: The page script (e.g., `shop.js`) calls a Service.
2. **Fetch**: `product.service.js` requests data from the API (or `products.json` in dev).
3. **Process**: The service validates the data and returns an Array to the script.
4. **Format**: The script loops through the data, passing each item to a **Template** (e.g., `product-card.html`).
5. **Inject**: The `TABLE` or a generic `RENDER` utility injects the final HTML into the DOM.

---

## 3. User Interaction Flows

### A. Dealer: Adding a New Product

1. Dealer clicks **"Add Product"** button.
2. `MODAL.open('productModal')` is triggered.
3. Dealer fills out the form and clicks **"Save"**.
4. `product.service.js` sends a `POST` request to the API.
5. **On Success**:
* `MODAL.close('productModal')`.
* `ALERT.show('Product Created', 'success')`.
* The Product Table re-renders to show the new entry.



### B. Client: Purchasing a Product

1. Client clicks **"Add to Cart"** on a `product-card`.
2. `UTILS.storageSave` updates the `dpt_shopping_cart` array.
3. The Navbar basket count updates via a DOM listener.
4. Client proceeds to `checkout.html`.
5. `order.service.js` processes the payment and clears the cart.

---

## 4. State Management (LocalStorage)

We use the browser's LocalStorage as a lightweight state manager for the following keys:

| Key | Purpose |
| --- | --- |
| `dpt_auth_token` | Maintains the session JWT for API calls. |
| `dpt_user_info` | Stores name, email, and role for UI personalization. |
| `dpt_shopping_cart` | Persists items in the cart across sessions. |
| `dpt_theme_mode` | Saves user preference for Light/Dark mode. |

---

## 5. Error Handling Flow

All API interactions are wrapped in `try/catch` blocks.

* **401 Unauthorized**: Wipes local storage and redirects to Login.
* **403 Forbidden**: Shows a "Permission Denied" alert.
* **500 Server Error**: Triggers `ALERT.show('System busy, try again later', 'danger')`.

---

### Next Step for the Project

To bring this flow to life, would you like me to create the **`assets/js/core/app.js`**? This file will act as the "orchestrator," initializing your components and running the authentication check as soon as any page loads.