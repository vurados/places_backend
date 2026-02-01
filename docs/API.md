# API Documentation

Complete API reference for the Urban Places Social App backend.

## Base URL

- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://{your_domain}/api/v1`

## Authentication

All authenticated endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

### Authentication Endpoints

#### Register User

**POST** `/auth/register`  
Creates a new user account.

**Request Body:**

```json
{
  "email": "john@example.com",
  "username": "johndoe",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Login (JSON)

**POST** `/auth/login`  
Authenticate and receive JWT token.

**Request Body:**

```json
{
  "login": "john@example.com", // can be email or username
  "password": "SecurePassword123!"
}
```

#### Login (OAuth2 Form)

**POST** `/auth/token`  
Standard OAuth2 login for compatibility (e.g., Swagger).

**Request Body**: `application/x-www-form-urlencoded`

- `username`: Email or username
- `password`: Password

#### Generic OAuth

**POST** `/auth/oauth`  
Used for mobile/client-side social login integration.

#### Delete Account

**DELETE** `/auth/delete-account`  
Deletes the current user's account. **Auth Required.**

---

## User Endpoints

### List Users

**GET** `/users/`  
**Auth Required.**

### Get Current User

**GET** `/users/me`  
**Auth Required.**

### Get User Profile

**GET** `/users/{user_id}`  
**Auth Required.**

---

## Place Endpoints

### List Places

**GET** `/places`  
Returns public places. Optional geo-filtering.

**Query Parameters:**

- `skip` / `limit` (int)
- `latitude` / `longitude` (float)
- `radius` (float)

### Create Place

**POST** `/places`  
**Auth Required.**

### Upload Place Photo

**POST** `/places/{place_id}/photos`  
Upload a photo specifically for a place. **Auth Required.**

---

## Search Endpoints

### Global Search

**GET** `/search/global?q=TEXT`  
Search users and places simultaneously.

### Search Users

**GET** `/search/users?q=TEXT`

### Search Places

**GET** `/search/places?q=TEXT`

---

## Friend Endpoints

### Get Friend Requests

**GET** `/friends/requests`  
Returns pending requests for current user.

### Send Friend Request

**POST** `/friends/requests`  
**Body**: `{"receiver_id": "uuid"}`

### Update Request Status

**PATCH** `/friends/requests/{request_id}`  
**Body**: `{"status": "accepted"}` // or "rejected"

### List Friends

**GET** `/friends/friends`  
Returns list of accepted friends.

---

## Messaging Endpoints

### Get Conversation

**GET** `/messages/{user_id}`  
Returns messages with a specific user.

### Send Message

**POST** `/messages/{user_id}`  
**Body**: `{"content": "text"}`

### Mark Message as Read

**PATCH** `/messages/{message_id}/read`

---

## Notification Endpoints

### Get Notifications

**GET** `/notifications`

### Mark Notification as Read

**PATCH** `/notifications/{notification_id}/read`

### Mark All as Read

**POST** `/notifications/read-all`

### Get Unread Count

**GET** `/notifications/unread-count`

---

## WebSockets

### Real-time Gateway

**WS** `/ws/ws?token=JWT_TOKEN`  
Supports `chat_message` and `typing` event types.

---

## Planned / Under Development

The following features have database models but currently **no API exposure**:

- **Routes**: `POST /routes` exists in docs but is not yet implemented in the API layer.
- **Reviews**: Database model `Review` exists.
- **Reactions**: Database model `Reaction` exists.
- **Collections**: Database model `Collection` exists.

---

## Error Responses

- `400 Bad Request`: Invalid input logic.
- `401 Unauthorized`: Missing or invalid token.
- `403 Forbidden`: Insufficient permissions.
- `404 Not Found`: Resource does not exist.
- `422 Validation Error`: JSON schema mismatch.
- `429 Too Many Requests`: Rate limit exceeded (10 req/s default).
