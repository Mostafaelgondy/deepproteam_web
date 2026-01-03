Creating an **API Contract** is a critical step for a project like **Deepproteam**. It ensures that the Frontend (which we've been building) and the Backend (API) speak the same language.

Here is a professional `docs/api-contracts.md` file. It defines the expected endpoints, request bodies, and response structures based on the mock data and components we've created.

---

# 🚀 Deepproteam API Contracts (v1.0)

This document defines the communication protocol between the Deepproteam frontend and the backend services.

## 1. Authentication Service

**Base Path:** `/api/auth`

### `POST /login`

Authenticates a user and returns a JWT.

* **Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}

```


* **Success Response (200):**
```json
{
  "token": "eyJhbG...",
  "user": { "id": "USR-01", "name": "John Doe", "role": "DEALER" }
}

```



---

## 2. Product Service

**Base Path:** `/api/products`

### `GET /`

Fetches a list of all products. Supports filtering by category and dealer.

* **Query Params:** `category`, `dealerId`, `status`
* **Success Response (200):** `Array<Product>` (See `assets/mock/products.json`)

### `POST /` (Dealer Only)

Creates a new product.

* **Request Body:**
```json
{
  "name": "String",
  "price": "Number",
  "category": "String",
  "description": "String",
  "tags": "Array<String>"
}

```



---

## 3. Order Service

**Base Path:** `/api/orders`

### `GET /dealer` (Dealer Only)

Fetches orders belonging to the authenticated dealer.

* **Success Response (200):** `Array<Order>` (See `assets/mock/orders.json`)

### `POST /checkout` (Client Only)

Converts a basket into a finalized order.

* **Request Body:**
```json
{
  "items": [{ "productId": "PRD-1001", "qty": 1 }],
  "paymentMethod": "Stripe"
}

```



---

## 4. Dealer Service

**Base Path:** `/api/dealers`

### `GET /profile`

Returns the profile details and subscription usage for the logged-in dealer.

* **Success Response (200):**
```json
{
  "companyName": "PixelPerfect",
  "subscription": {
    "plan": "Professional",
    "slotsUsed": 24,
    "slotsTotal": 50,
    "nextBilling": "2026-11-15"
  }
}

```



---

## 5. Global Error Object

All error responses (4xx, 5xx) follow this standard:

```json
{
  "error": true,
  "code": "AUTH_EXPIRED",
  "message": "Your session has expired. Please login again."
}

```

---

### Implementation Guidelines for Developers:

1. **Headers**: All protected routes require `Authorization: Bearer <token>`.
2. **Versioning**: Future breaking changes must increment the path to `/api/v2/...`.
3. **Dates**: All dates must be returned in ISO 8601 format (`YYYY-MM-DDTHH:mm:ssZ`).

---

### Next Logical Step

Now that the contract is defined, would you like me to create **`assets/js/services/api.service.js`**? This file will be the actual code that implements these contracts, handling all `fetch` requests and error handling in one place.