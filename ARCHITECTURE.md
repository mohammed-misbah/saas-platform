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


# ==========================================
# Phase 5 - File Management Architecture
# ==========================================

## File Upload Flow

User

↓

Authentication

↓

Role Validation

↓

Tenant Validation

↓

Project Validation

↓

Archived Project Validation

↓

File Extension Validation

↓

File Size Validation

↓

Upload to AWS S3

↓

Store Metadata in Database

↓

Audit Log

↓

Return Response

---

## File Download Flow

User

↓

Authentication

↓

Permission Validation

↓

Tenant Validation

↓

Generate AWS Pre-Signed URL

↓

Audit Log

↓

Return URL

---

## File Delete Flow

User

↓

Authentication

↓

Permission Validation

↓

Tenant Validation

↓

Member Ownership Validation

↓

Delete Object from AWS S3

↓

Delete Database Record

↓

Audit Log

↓

Return Response

---

# Storage Rules

Files are stored using

company-{company_id}/project-{project_id}/{uuid}_{filename}

Example

company-5/project-12/e12ac9fd_contract.pdf

Benefits

- Unique filenames
- No duplicate uploads
- Company isolation
- Project separation
- Easy storage management

---

# Tenant Isolation

Company A

×

Cannot access Company B files

×

Cannot download Company B files

×

Cannot delete Company B files

Company B

×

Cannot access Company A files

---

# Permission Matrix

| Feature | Super Admin | Company Admin | Member |
|----------|-------------|---------------|--------|
| Upload File | ✅ | ✅ | ✅ |
| View Files | ✅ | ✅ | Assigned Projects Only |
| Download File | ✅ | ✅ | Assigned Projects Only |
| Delete File | ✅ | ✅ | Own Uploaded Files Only |
| View Company Files | ✅ | Own Company | ❌ |
| View Other Company Files | ✅ | ❌ | ❌ |

---

# File Validation Rules

Maximum Size

10 MB

Allowed Extensions

- pdf
- doc
- docx
- xls
- xlsx
- jpg
- jpeg
- png
- txt

Blocked Examples

- exe
- bat
- dll
- sh
- cmd