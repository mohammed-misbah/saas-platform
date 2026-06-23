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


# API Documentation — Phase 4

## Authentication

All APIs require Bearer Token authentication.

Header:
Authorization: Bearer <token>

---

# Companies APIs

## Create Company

POST /companies/

Access:

* Super Admin only

Request:

```json
{
  "company_name": "ABC Technologies",
  "slug": "abc-tech"
}
```

Response:

```json
{
  "id": 1,
  "company_name": "ABC Technologies",
  "slug": "abc-tech"
}
```

---

## Get Company

GET /companies/{company_id}

Access:

* Super Admin only

---

## Update Company

PUT /companies/{company_id}

Access:

* Super Admin only

---

## Delete Company

DELETE /companies/{company_id}

Access:

* Super Admin only

Condition:

* Company must not contain users

---

# Users APIs

## Create User

POST /users/create

Access:

* Super Admin
* Company Admin

Rules:

* Company Admin can only create Members

Request:

```json
{
  "email": "member@test.com",
  "password": "123456",
  "role_id": 3
}
```

---

## Update User

PUT /users/{user_id}

Access:

* Super Admin
* Company Admin

Rules:

* Company Admin can only update users inside own company
* Company Admin cannot assign Admin roles

---

## Delete User

DELETE /users/{user_id}

Access:

* Super Admin
* Company Admin

Rules:

* Cannot delete self

---

## Get User

GET /users/{user_id}

Access:

* Super Admin
* Company Admin

---

## Get User List

GET /users/

Access:

* Super Admin
* Company Admin

---

# Projects APIs

## Create Project

POST /projects/create

Access:

* Super Admin
* Company Admin

---

## Get Project

GET /projects/{project_id}

Access:

* Super Admin
* Company Admin

Tenant Isolation enabled.

---

## Get Project List

GET /projects/

Access:

* Super Admin
* Company Admin

Tenant Isolation enabled.

---

## Update Project

PUT /projects/{project_id}

Access:

* Super Admin
* Company Admin

Includes:

* Project status validation
* Project flow validation

---

## Delete Project

DELETE /projects/{project_id}

Access:

* Super Admin
* Company Admin

---

# Project Assignment APIs

## Assign User to Project

POST /assign_projects/{project_id}/members

Access:

* Super Admin
* Company Admin

Rules:

* User must belong to same company
* Only Members can be assigned

---

## Get Project Members

GET /assign_projects/{project_id}/members

Access:

* Super Admin
* Company Admin

---

## Remove User from Project

DELETE /assign_projects/{project_id}/members/{user_id}

Access:

* Super Admin
* Company Admin

