System Name:
SaaS Platform

Features:

1. Company Registration
2. User Management
3. Role Management
4. Project Management
5. File Upload
6. Notifications
7. Audit Logs


# API Documentation

## Authentication

### Register User

**POST** `/auth/register`

Request:

```json
{
  "email": "user@test.com",
  "password": "password123",
  "role_id": 3
}
```

Response:

```json
{
  "id": 1,
  "email": "user@test.com"
}
```

---

### Login User

**POST** `/auth/login`

Request:

```json
{
  "email": "user@test.com",
  "password": "password123"
}
```

Response:

```json
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

---

## Users

### Current User

**GET** `/users/me`

Header:

```text
Authorization: Bearer <jwt_token>
```

Response:

```json
{
  "id": 1,
  "email": "user@test.com",
  "is_active": true
}
```
