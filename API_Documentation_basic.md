# API Documentation (Updated) — Employee Shift Roster System

This document describes the REST API endpoints and request/response formats based on your current SQLite schema.

---

## 📋 API Endpoint Summary

| Resource            | Method | Endpoint                | Description                        |
|---------------------|--------|-------------------------|------------------------------------|
| Authentication      | POST   | /login                  | User login                         |
| Users/Employees     | GET    | /users                  | Get all users                      |
|                     | POST   | /users                  | Create a new user                  |
| Shift Roster        | GET    | /shift_roster           | Get all shift assignments          |
|                     | POST   | /shift_roster           | Create a new shift assignment      |
| Leave Requests      | GET    | /leave_requests         | Get all leave requests             |
|                     | POST   | /leave_requests         | Create a new leave request         |
| Timesheets          | GET    | /timesheets             | Get all timesheets                 |
|                     | POST   | /timesheets             | Create a new timesheet entry       |
| Areas               | GET    | /area                   | Get all work areas                 |
|                     | POST   | /area                   | Create a new work area             |
| Designations        | GET    | /designations           | Get all designations               |
|                     | POST   | /designations           | Create a new designation           |
| Roles               | GET    | /roles                  | Get all roles                      |
|                     | POST   | /roles                  | Create a new role                  |
| Skills              | GET    | /skills                 | Get all skills                     |
|                     | POST   | /skills                 | Create a new skill                 |
| Licenses            | GET    | /licenses               | Get all licenses                   |
|                     | POST   | /licenses               | Create a new license               |
| Community Posts     | GET    | /community_posts        | Get all community posts            |
|                     | POST   | /community_posts        | Create a new community post        |
| Activity Logs       | GET    | /activity_logs          | Get all activity logs              |

---



## 🔐 Authentication

All endpoints (except login) require JWT authentication.  
Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

---

## 👥 Users & Employees

### GET /users
Get all users.

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "name": "John",
      "surname": "Doe",
      "email": "john.doe@company.com",
      "contact_no": "+1234567890",
      "alt_contact_name": "Jane Doe",
      "alt_contact_no": "+1234567899",
      "role_id": 2,
      "designation_id": 1,
      "area_of_responsibility_id": 1,
      "hire_date": "2024-01-15",
      "is_active": true,
      "rate_type": "hourly",
      "rate_value": 25,
      "total_no_leave_days_annual": 15,
      "total_no_leave_days_annual_float": 15.0
    }
  ]
}
```

### POST /users
Create a new user.

**Request Body:**
```json
{
  "name": "Jane",
  "surname": "Smith",
  "email": "jane.smith@company.com",
  "contact_no": "+1234567891",
  "alt_contact_name": "John Smith",
  "alt_contact_no": "+1234567899",
  "role_id": 2,
  "designation_id": 1,
  "area_of_responsibility_id": 1,
  "hire_date": "2024-02-01",
  "is_active": true,
  "rate_type": "hourly",
  "rate_value": 25,
  "total_no_leave_days_annual": 15,
  "total_no_leave_days_annual_float": 15.0
}
```

---

## 📅 Shift Roster

### GET /shift_roster
Get all shift assignments.

**Response:**
```json
{
  "roster": [
    {
      "id": 1,
      "employee_id": 1,
      "shift_id": 1,
      "date": "2024-01-15",
      "hours": 8,
      "status": "approved",
      "notes": "Covering for sick leave",
      "area_of_responsibility_id": 2,
      "accepted_at": "2024-01-15T10:00:00Z",
      "created_at": "2024-01-14T09:00:00Z"
    }
  ]
}
```

### POST /shift_roster
Create a new shift assignment.

**Request Body:**
```json
{
  "employee_id": 1,
  "shift_id": 1,
  "date": "2024-01-16",
  "hours": 8,
  "status": "pending",
  "notes": "Covering for sick leave",
  "area_of_responsibility_id": 2
}
```

---

## 🗓️ Leave Requests

### GET /leave_requests
Get all leave requests.

**Response:**
```json
{
  "leave_requests": [
    {
      "id": 1,
      "employee_id": 1,
      "leave_type": "Unpaid",
      "start_date": "2025-08-13",
      "end_date": "2025-08-14",
      "days": 2,
      "reason": "Documentation required",
      "status": "approved",
      "approved_by": 1,
      "approved_at": "2025-08-13T18:18:17.714Z",
      "created_at": "2025-08-13T18:17:31.199Z",
      "action_comment": "Urgent leave needed",
      "no_of_leave_days_remaining": 10,
      "authorised_by": 2,
      "authorised_at": "2025-08-13T18:18:17.714Z",
      "attachment_url": "https://.../file.pdf"
    }
  ]
}
```

### POST /leave_requests
Create a new leave request.

**Request Body:**
```json
{
  "employee_id": 1,
  "leave_type": "Unpaid",
  "start_date": "2025-08-13",
  "end_date": "2025-08-14",
  "days": 2,
  "reason": "Documentation required",
  "action_comment": "Urgent leave needed",
  "authorised_by": 2,
  "attachment": "<file upload>"
}
```
*Note: For attachments, use `multipart/form-data`.*

---

## 🕒 Timesheets

### GET /timesheets
Get all timesheets.

**Response:**
```json
{
  "timesheets": [
    {
      "id": 1,
      "employee_id": 1,
      "roster_id": 2,
      "date": "2024-01-16",
      "hours_worked": 8,
      "status": "approved",
      "notes": "Worked extra hour",
      "accepted_at": "2024-01-16T18:00:00Z"
    }
  ]
}
```

### POST /timesheets
Create a new timesheet entry.

**Request Body:**
```json
{
  "employee_id": 1,
  "roster_id": 2,
  "date": "2024-01-16",
  "hours_worked": 8,
  "status": "approved",
  "notes": "Worked extra hour"
}
```

---

## 🏢 Areas & Designations

### GET /area
Get all work areas.

**Response:**
```json
{
  "areas": [
    {
      "area_id": 1,
      "name": "Kitchen"
    },
    {
      "area_id": 2,
      "name": "Service"
    }
  ]
}
```

### POST /area
Create a new work area.

**Request Body:**
```json
{
  "name": "Bakery"
}
```

### GET /designations
Get all designations.

**Response:**
```json
{
  "designations": [
    {
      "designation_id": 1,
      "name": "Chef"
    }
  ]
}
```

### POST /designations
Create a new designation.

**Request Body:**
```json
{
  "name": "Supervisor"
}
```

---

## 🛡️ Roles

### GET /roles
Get all roles.

**Response:**
```json
{
  "roles": [
    {
      "id": 1,
      "name": "Admin"
    },
    {
      "id": 2,
      "name": "Manager"
    }
  ]
}
```

### POST /roles
Create a new role.

**Request Body:**
```json
{
  "name": "Supervisor"
}
```

---

## 🏷️ Skills

### GET /skills
Get all skills.

**Response:**
```json
{
  "skills": [
    {
      "id": 1,
      "name": "Food Preparation"
    }
  ]
}
```

### POST /skills
Create a new skill.

**Request Body:**
```json
{
  "name": "Customer Service"
}
```

---

## 📄 Licenses

### GET /licenses
Get all licenses.

**Response:**
```json
{
  "licenses": [
    {
      "id": 1,
      "name": "Food Safety Certificate"
    }
  ]
}
```

### POST /licenses
Create a new license.

**Request Body:**
```json
{
  "name": "First Aid Certificate"
}
```

---

## 📚 Community Posts & Activity Logs

### GET /community_posts
Get all community posts.

**Response:**
```json
{
  "community_posts": [
    {
      "id": 1,
      "user_id": 1,
      "content": "Welcome to the team!"
    }
  ]
}
```

### POST /community_posts
Create a new community post.

**Request Body:**
```json
{
  "user_id": 1,
  "content": "Welcome to the team!"
}
```

### GET /activity_logs
Get all activity logs.

**Response:**
```json
{
  "activity_logs": [
    {
      "id": 1,
      "user_id": 1,
      "action": "Logged in",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

## ❌ Error Responses

**Standard Error Format:**
```json
{
  "error": "Error message description",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

**Common Error Codes:**
- `INVALID_CREDENTIALS`
- `TOKEN_EXPIRED`
- `INSUFFICIENT_PERMISSIONS`
- `VALIDATION_ERROR`
- `RESOURCE_NOT_FOUND`
- `DUPLICATE_ENTRY`

---

## 📝 Notes

- All endpoints require JWT authentication unless otherwise noted.
- For file uploads (attachments), use `multipart/form-data`.
- Optional fields are marked in request bodies.
- Pagination, filtering, and sorting can be added via query parameters for list endpoints.

---



This documentation is generated from your current database schema.  
Update