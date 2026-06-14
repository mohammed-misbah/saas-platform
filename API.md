# API Documentation

## Authentication

### Login

POST /auth/login

Request

{
"email": "[admin@test.com](mailto:admin@test.com)",
"password": "123456"
}

Response

{
"access_token": "...",
"token_type": "bearer"
}

---

## Current User

GET /users/me

Response

{
"id": 1,
"email": "[admin@test.com](mailto:admin@test.com)",
"is_active": true
}

---

## Companies

### Create Company

POST /companies

Permission:

Super Admin only

---

### Get Company

GET /companies/{id}

Permission:

Super Admin only

---

### Update Company

PUT /companies/{id}

Permission:

Super Admin only

---

### Delete Company

DELETE /companies/{id}

Permission:

Super Admin only

---

## Users

### Create User

POST /users/create

Permission:

* Super Admin
* Company Admin

---

### Get User

GET /users/{id}

Permission:

* Super Admin
* Company Admin

---

### List Users

GET /users

Permission:

* Super Admin
* Company Admin

---

### Update User

PUT /users/{id}

Permission:

* Super Admin
* Company Admin

---

### Delete User

DELETE /users/{id}

Permission:

* Super Admin
* Company Admin

---

## Health Check

GET /health

Response

{
"status": "healthy"
}
