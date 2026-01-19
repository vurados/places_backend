# API Documentation

Complete API reference for the Urban Places Social App backend.

## Base URL

- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://yourdomain.com/api/v1`

## Authentication

All authenticated endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

### Obtain JWT Token

**POST** `/auth/login`

```json
{
  "username": "user@example.com",
  "password": "your-password"
}
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

---

## Endpoints Overview

| Category | Endpoint | Method | Auth Required |
|----------|----------|--------|---------------|
| [Authentication](#authentication-endpoints) | `/auth/register` | POST | No |
| | `/auth/login` | POST | No |
| [Users](#user-endpoints) | `/users/me` | GET | Yes |
| | `/users/{user_id}` | GET | Yes |
| [Places](#place-endpoints) | `/places` | GET, POST | Yes |
| | `/places/{place_id}` | GET, PUT, DELETE | Yes |
| [Friends](#friend-endpoints) | `/friends/requests` | GET, POST | Yes |
| | `/friends` | GET | Yes |
| [Messages](#message-endpoints) | `/messages` | GET, POST | Yes |
| [Routes](#route-endpoints) | `/routes` | GET, POST | Yes |
| | `/routes/{route_id}` | GET, PUT, DELETE | Yes |
| [Photos](#photo-endpoints) | `/photos/upload` | POST | Yes |
| [Notifications](#notification-endpoints) | `/notifications` | GET | Yes |

---

## Authentication Endpoints

### Register User

**POST** `/auth/register`

Creates a new user account.

**Request Body:**

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

**Response:** `201 Created`

```json
{
  "id": "uuid",
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-14T10:00:00Z"
}
```

### Login

**POST** `/auth/login`

Authenticate and receive JWT token.

**Request Body:**

```json
{
  "username": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

---

## User Endpoints

### Get Current User

**GET** `/users/me`

Returns the authenticated user's profile.

**Headers:**

```
Authorization: Bearer <token>
```

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "bio": "Tech enthusiast",
  "avatar_url": "https://...",
  "created_at": "2024-01-14T10:00:00Z"
}
```

### Update Profile

**PUT** `/users/me`

Update the current user's profile.

**Request Body:**

```json
{
  "full_name": "John Updated",
  "bio": "New bio"
}
```

---

## Place Endpoints

### List Places

**GET** `/places`

Get a list of places with optional filters.

**Query Parameters:**

- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Max records to return (default: 100)
- `lat` (float): Latitude for location-based search
- `lon` (float): Longitude for location-based search
- `radius` (float): Search radius in kilometers

**Response:** `200 OK`

```json
[
  {
    "id": "uuid",
    "name": "Central Park",
    "description": "Beautiful park in the city",
    "lat": 40.785091,
    "lon": -73.968285,
    "address": "New York, NY",
    "category": "park",
    "created_by": "uuid",
    "created_at": "2024-01-14T10:00:00Z",
    "photos": []
  }
]
```

### Create Place

**POST** `/places`

Create a new place.

**Request Body:**

```json
{
  "name": "My Favorite Cafe",
  "description": "Great coffee shop",
  "lat": 40.7580,
  "lon": -73.9855,
  "address": "123 Main St, New York",
  "category": "cafe"
}
```

**Response:** `201 Created`

### Get Place Details

**GET** `/places/{place_id}`

Get detailed information about a specific place.

**Response:** `200 OK`

---

## Friend Endpoints

### Send Friend Request

**POST** `/friends/requests`

Send a friend request to another user.

**Request Body:**

```json
{
  "user_id": "uuid-of-target-user"
}
```

**Response:** `201 Created`

### Get Friend Requests

**GET** `/friends/requests`

Get pending friend requests (sent and received).

**Response:** `200 OK`

```json
{
  "sent": [],
  "received": [
    {
      "id": "uuid",
      "from_user": {
        "id": "uuid",
        "username": "alice",
        "full_name": "Alice Smith"
      },
      "status": "pending",
      "created_at": "2024-01-14T10:00:00Z"
    }
  ]
}
```

### Accept/Reject Friend Request

**PUT** `/friends/requests/{request_id}`

**Request Body:**

```json
{
  "action": "accept"  // or "reject"
}
```

---

## Message Endpoints

### Send Message

**POST** `/messages`

Send a message to a friend.

**Request Body:**

```json
{
  "receiver_id": "uuid",
  "content": "Hello! How are you?"
}
```

**Response:** `201 Created`

### Get Messages

**GET** `/messages`

Get conversation with a specific user.

**Query Parameters:**

- `user_id` (uuid): ID of the conversation partner
- `skip` (int): Pagination offset
- `limit` (int): Max messages to return

---

## Route Endpoints

### Create Route

**POST** `/routes`

Create a new route with multiple places.

**Request Body:**

```json
{
  "name": "NYC Food Tour",
  "description": "Best restaurants in Manhattan",
  "places": ["place-uuid-1", "place-uuid-2", "place-uuid-3"]
}
```

### Get User Routes

**GET** `/routes`

Get all routes created by the current user.

---

## Photo Endpoints

### Upload Photo

**POST** `/photos/upload`

Upload a photo to MinIO storage.

**Request:**

- Content-Type: `multipart/form-data`
- Body: `file` (image file)
- Optional: `place_id` (uuid) to associate with a place

**Response:** `201 Created`

```json
{
  "id": "uuid",
  "url": "https://minio.../photo.jpg",
  "uploaded_at": "2024-01-14T10:00:00Z"
}
```

---

## Notification Endpoints

### Get Notifications

**GET** `/notifications`

Get all notifications for the current user.

**Response:** `200 OK`

```json
[
  {
    "id": "uuid",
    "type": "friend_request",
    "message": "Alice sent you a friend request",
    "read": false,
    "created_at": "2024-01-14T10:00:00Z"
  }
]
```

### Mark as Read

**PUT** `/notifications/{notification_id}/read`

Mark a notification as read.

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden

```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

API requests are rate-limited via Nginx:

- **Default**: 10 requests/second per IP
- **Burst**: Up to 20 requests
- Exceeding limits returns `429 Too Many Requests`

---

## Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to test endpoints directly from your browser!

---

## Example: Complete Authentication Flow

### 1. Register

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. Use Token

```bash
TOKEN="<your-token-from-login>"

curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## WebSocket Support

*(Future feature)* Real-time messaging via WebSocket connections.

---

## Need Help?

- Check the [Development Guide](DEVELOPMENT.md) for local setup
- Review [Deployment Guide](DEPLOYMENT.md) for production setup
- See FastAPI docs: <https://fastapi.tiangolo.com/>
