# Architecture Documentation

## System Type

Multi-Tenant SaaS Platform

---

## Tenant Isolation

Tenant isolation is the core security rule of the application.

Users must never access data belonging to another company.

Example:

Company A

* Ali
* Ahmed

Company B

* John
* David

When Ali logs in:

Allowed:

* Ali
* Ahmed

Not Allowed:

* John
* David

All company-scoped queries must filter using:

company_id

Example:

Bad

SELECT * FROM users

Good

SELECT *
FROM users
WHERE company_id = current_user.company_id

---

## Role Hierarchy

### Super Admin

Platform-level administrator.

Permissions:

* Create Company
* Update Company
* Delete Company
* View All Companies
* Create User
* Update User
* Delete User
* View All Users

Super Admin can access all companies and all users.

---

### Company Admin

Company-level administrator.

Permissions:

* Create User
* Update User
* Delete User
* View Users

Restrictions:

* Cannot create companies
* Cannot update companies
* Cannot delete companies
* Can only access users belonging to own company

---

### Member

Standard application user.

Permissions:

* Login
* Use Application Features

Restrictions:

* Cannot create users
* Cannot update users
* Cannot delete users
* Cannot create companies
* Cannot update companies
* Cannot delete companies

---

## User Ownership

Every user belongs to exactly one company.

Example:

[john@test.com](mailto:john@test.com)
↓
ABC Trading

Multi-company users are not supported.

---

## Audit Logging

Every important action is stored in audit_logs.

Examples:

* User Created
* User Updated
* User Deleted
* Company Created
* Company Updated
* Company Deleted

Purpose:

* Security
* Compliance
* Troubleshooting
* Change Tracking

Audit logs record:

* Who performed the action
* Which company was affected
* What action occurred
* When it occurred

---

## Authentication

Authentication uses JWT Bearer Tokens.

Flow:

Login
↓
JWT Token Issued
↓
Protected API Access
↓
Current User Retrieved

---

## Authorization

Authorization is role-based.

Every protected endpoint validates the current user's role before performing an action.

Example:

Company creation:

Super Admin → Allowed

Company Admin → Denied

Member → Denied
