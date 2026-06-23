# Database Documentation

## Tables

### users

| Column        | Type                       |
| ------------- | -------------------------- |
| id            | Integer                    |
| email         | String                     |
| password_hash | String                     |
| is_active     | Boolean                    |
| role_id       | Foreign Key → roles.id     |
| company_id    | Foreign Key → companies.id |
| created_at    | DateTime                   |
| updated_at    | DateTime                   |

---

### roles

| Column    | Type    |
| --------- | ------- |
| id        | Integer |
| role_name | String  |

Roles:

* Super Admin
* Company Admin
* Member

---

### companies

| Column       | Type     |
| ------------ | -------- |
| id           | Integer  |
| company_name | String   |
| slug         | String   |
| is_active    | Boolean  |
| created_at   | DateTime |
| updated_at   | DateTime |

---

### audit_logs

| Column     | Type                       |
| ---------- | -------------------------- |
| id         | Integer                    |
| user_id    | Foreign Key → users.id     |
| company_id | Foreign Key → companies.id |
| action     | String                     |
| created_at | DateTime                   |

Examples:

* Created company ABC Trading
* Updated company ABC Trading
* Deleted company ABC Trading
* Created user [john@test.com](mailto:john@test.com)
* Updated user [john@test.com](mailto:john@test.com)
* Deleted user [john@test.com](mailto:john@test.com)

---

## Relationships

### User → Role

One user belongs to one role.

Example:

User:
[john@test.com](mailto:john@test.com)

Role:
Company Admin

---

### User → Company

One user belongs to one company.

Example:

[john@test.com](mailto:john@test.com)
↓
ABC Trading

---

### Company → Users

One company can have many users.

Example:

ABC Trading
├── Company Admin
├── Ahmed
├── Ali
└── Rahman

---

### Audit Log → User

Every audit log stores which user performed the action.

Example:

Ali created Ahmed

Audit Log:

user_id = Ali
action = Created user Ahmed



# Database Documentation — Phase 4

## companies

| Column       | Type    |
| ------------ | ------- |
| id           | Integer |
| company_name | String  |
| slug         | String  |
| is_active    | Boolean |

---

## roles

| Column    | Type    |
| --------- | ------- |
| id        | Integer |
| role_name | String  |

Roles:

* Super Admin
* Company Admin
* Member

---

## users

| Column        | Type    |
| ------------- | ------- |
| id            | Integer |
| email         | String  |
| password_hash | String  |
| role_id       | FK      |
| company_id    | FK      |
| is_active     | Boolean |

Relations:

* user belongs to role
* user belongs to company

---

## projects

| Column       | Type    |
| ------------ | ------- |
| id           | Integer |
| project_name | String  |
| description  | Text    |
| status       | String  |
| company_id   | FK      |
| created_by   | FK      |

Relations:

* project belongs to company
* project created by user

---

## project_members

| Column     | Type    |
| ---------- | ------- |
| id         | Integer |
| project_id | FK      |
| user_id    | FK      |

Relations:

* project linked to many users

---

## audit_logs

| Column     | Type     |
| ---------- | -------- |
| id         | Integer  |
| user_id    | FK       |
| company_id | FK       |
| action     | String   |
| created_at | DateTime |

Stores all important system actions.
