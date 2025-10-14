# API Documentation - Employee Shift Roster System

This document provides comprehensive documentation for all API endpoints in the Employee Shift Roster application.

## 🔐 Authentication

All API endpoints (except login and test endpoints) require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Authentication Flow

1. **Login** with credentials or Google OAuth
2. **Receive** JWT access token and refresh token
3. **Include** access token in all subsequent requests
4. **Refresh** token when it expires

## 📋 Base URL

- **Development**: `http://localhost:5001/api`
- **Production**: `https://your-domain.com/api`

---

# 🔑 Authentication Endpoints

## POST /auth/google
Google OAuth authentication.

**Request Body:**
```json
{
  "credential": "google-oauth-credential"
}
```

**Response:**
```json
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@company.com",
    "role": "Admin"
  }
}
```

## POST /auth/login
Login with username/email and password.

**Request Body:**
```json
{
  "username": "admin@company.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "user": {
    "id": 1,
    "name": "Admin User",
    "email": "admin@company.com",
    "role": "Admin"
  }
}
```

## POST /auth/refresh
Refresh JWT token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "your-refresh-token"
}
```

**Response:**
```json
{
  "access_token": "new-jwt-token"
}
```

## GET /auth/me
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@company.com",
  "role": "Admin",
  "employee_id": "EMP001"
}
```

## POST /auth/logout
Logout and invalidate token.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

---

# 👥 Employee Management Endpoints

## GET /employees
Get all employees with filtering and pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10)
- `search`: Search term for name/email
- `role_id`: Filter by role ID
- `area_id`: Filter by area ID

**Response:**
```json
{
  "employees": [
    {
      "id": 1,
      "name": "John",
      "surname": "Doe",
      "email": "john@company.com",
      "employee_id": "EMP001",
      "role": {
        "id": 1,
        "name": "Admin"
      },
      "area_of_responsibility": {
        "id": 1,
        "name": "Management"
      }
    }
  ],
  "total": 50,
  "pages": 5,
  "current_page": 1
}
```

## POST /employees
Create a new employee.

**Request Body:**
```json
{
  "name": "John",
  "surname": "Doe",
  "email": "john@company.com",
  "employee_id": "EMP001",
  "contact_no": "+1234567890",
  "role_id": 1,
  "area_of_responsibility_id": 1,
  "designation_id": 1
}
```

## GET /employees/{employee_id}
Get a specific employee by ID.

## PUT /employees/{employee_id}
Update an employee.

## DELETE /employees/{employee_id}
Delete an employee.

## POST /employees/{employee_id}/skills
Add a skill to an employee.

## DELETE /employees/{employee_id}/skills/{skill_id}
Remove a skill from an employee.

## GET /employees/{employee_id}/licenses
Get employee licenses.

## POST /employees/{employee_id}/licenses
Add a license to an employee.

## PUT /employees/{employee_id}/licenses/{license_id}
Update employee license (e.g., expiry date).

## DELETE /employees/{employee_id}/licenses/{license_id}
Remove license from employee.

## POST /employees/{employee_id}/reset-password
Reset employee password.

## POST /employees/{employee_id}/generate-password
Generate a new password for employee.

## GET /employees/{employee_id}/password-info
Get password information for employee.

---

# 🏢 Admin Management Endpoints

## Roles Management

### GET /roles
Get all roles.

### POST /roles
Create a new role.

**Request Body:**
```json
{
  "name": "Manager",
  "description": "Department manager role",
  "permissions": {
    "can_approve_leave": true,
    "can_manage_schedules": true
  }
}
```

### PUT /roles/{role_id}
Update a role.

### DELETE /roles/{role_id}
Delete a role.

## Areas of Responsibility

### GET /areas
Get all areas of responsibility.

### POST /areas
Create a new area.

**Request Body:**
```json
{
  "name": "IT Department",
  "description": "Information Technology",
  "color": "#3498db"
}
```

### PUT /areas/{area_id}
Update an area.

### DELETE /areas/{area_id}
Delete an area.

## Skills Management

### GET /skills
Get all skills.

### POST /skills
Create a new skill.

**Request Body:**
```json
{
  "name": "JavaScript",
  "description": "Programming language",
  "category": "Programming"
}
```

### PUT /skills/{skill_id}
Update a skill.

### DELETE /skills/{skill_id}
Delete a skill.

## Shifts Management

### GET /shifts
Get all shifts.

### POST /shifts
Create a new shift.

**Request Body:**
```json
{
  "name": "Day Shift",
  "start_time": "08:00",
  "end_time": "17:00",
  "hours": 8.0,
  "color": "#2ecc71"
}
```

### PUT /shifts/{shift_id}
Update a shift.

### DELETE /shifts/{shift_id}
Delete a shift.

## Licenses Management

### GET /licenses
Get all available licenses.

### POST /licenses
Create a new license type.

**Request Body:**
```json
{
  "name": "Driver's License",
  "description": "Valid driving license"
}
```

## Hourly Rates Management

### GET /hourly-rates
Get all hourly rates with employee information.

**Response:**
```json
{
  "rates": [
    {
      "rate_id": 1,
      "employee_id": 1,
      "employee_name": "John Doe",
      "employee_code": "EMP001",
      "rate_per_hr": 125.50,
      "currency": "ZAR",
      "effective_date": "2024-01-01",
      "end_date": null
    }
  ],
  "total": 48
}
```

### POST /hourly-rates
Create a new hourly rate.

**Request Body:**
```json
{
  "employee_id": 1,
  "rate_per_hr": 125.50,
  "currency": "ZAR",
  "effective_date": "2024-01-01"
}
```

### PUT /hourly-rates/{rate_id}
Update an hourly rate.

### DELETE /hourly-rates/{rate_id}
End an hourly rate (set end_date).

### GET /hourly-rates/employees
Get employees available for rate assignment.

---

# 📊 Analytics Endpoints

## GET /analytics/dashboard
Get dashboard metrics overview.

**Response:**
```json
{
  "total_employees": 50,
  "active_employees": 48,
  "total_shifts": 12,
  "pending_leave_requests": 5,
  "approved_timesheets": 120
}
```

## GET /analytics/skill-distribution
Get skill distribution across employees.

## GET /analytics/weekly-approval-trends
Get weekly approval trends for timesheets/leave.

## GET /analytics/employees-by-shift
Get employee distribution by shift.

## GET /analytics/employees-by-role
Get employee distribution by role.

## GET /analytics/employees-by-area
Get employee distribution by area.

## GET /analytics/leave-summary
Get leave request summary statistics.

## GET /analytics/skill-search
Search employees by skills.

**Query Parameters:**
- `skills`: Comma-separated skill names

## GET /analytics/shift-coverage
Get shift coverage analysis.

## GET /analytics/employee-availability
Get employee availability analysis.

## Cost Analytics (Admin Only)

### GET /analytics/costs/overview
Get cost overview metrics.

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

### GET /analytics/costs/by-area
Get costs breakdown by area.

### GET /analytics/costs/by-designation
Get costs breakdown by designation.

### GET /analytics/costs/by-employee
Get costs breakdown by employee.

### GET /analytics/costs/daily-trends
Get daily cost trends.

### GET /analytics/costs/efficiency
Get cost efficiency metrics.

---

# 🗓️ Leave Management Endpoints

## GET /leave
Get leave requests with filtering.

**Query Parameters:**
- `status`: Filter by status (pending, approved, rejected)
- `employee_id`: Filter by employee
- `start_date`: Filter by date range
- `end_date`: Filter by date range

## POST /leave
Create a new leave request.

**Request Body:**
```json
{
  "start_date": "2024-03-01",
  "end_date": "2024-03-05",
  "leave_type": "annual",
  "reason": "Family vacation",
  "days_requested": 5
}
```

## POST /leave/{request_id}/approve
Approve a leave request.

## POST /leave/{request_id}/authorise
Authorize a leave request (final approval).

## POST /leave/{request_id}/action
Take action on leave request (approve/reject).

**Request Body:**
```json
{
  "action": "approve",
  "comment": "Approved for vacation"
}
```

## DELETE /leave/{request_id}
Delete a leave request.

## GET /leave/{request_id}/attachment
Get leave request attachment.

## POST /leave/{request_id}/attachment
Upload attachment for leave request.

## DELETE /leave/{request_id}/attachment
Delete leave request attachment.

## GET /leave/{request_id}/attachment/download
Download leave request attachment.

## GET /leave/pending-count
Get count of pending leave requests.

---

# ⏱️ Timesheet Endpoints

## GET /timesheets
Get timesheets with filtering.

## POST /timesheets
Create a new timesheet entry.

## PUT /timesheets/{timesheet_id}
Update a timesheet entry.

## DELETE /timesheets/{timesheet_id}
Delete a timesheet entry.

---

# 📄 Export Endpoints

## GET /export/employees
Export employees data to Excel.

**Query Parameters:**
- `format`: Export format (excel, csv)

## GET /export/leave-requests
Export leave requests to Excel.

**Query Parameters:**
- `start_date`: Start date filter
- `end_date`: End date filter
- `status`: Status filter

---

# 📋 Reports Endpoints

## GET /reports/employee-summary
Get employee summary report.

## GET /reports/leave-summary
Get leave summary report.

## GET /reports/timesheet-summary
Get timesheet summary report.

---

# 🏗️ Roster Management Endpoints

## GET /roster
Get roster schedules.

## POST /roster
Create roster entries.

## PUT /roster/{roster_id}
Update roster entry.

## DELETE /roster/{roster_id}
Delete roster entry.

---

# 🏢 Designations Endpoints

## GET /designations
Get all job designations.

## POST /designations
Create a new designation.

## PUT /designations/{designation_id}
Update a designation.

## DELETE /designations/{designation_id}
Delete a designation.

---

# 🏪 Licenses Endpoints

## GET /licenses
Get all license types.

## POST /licenses
Create a new license type.

---

# 🌐 Community Endpoints

Community-related endpoints for employee interaction and communication.

---

# ❌ Error Responses

All endpoints may return the following error responses:

## 400 Bad Request
```json
{
  "error": "Validation failed",
  "details": {
    "field": ["Field is required"]
  }
}
```

## 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Valid token required"
}
```

## 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

## 404 Not Found
```json
{
  "error": "Resource not found"
}
```

## 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Please contact support"
}
```

---

# 📝 Notes

1. **Authentication**: All endpoints except `/auth/login` and `/auth/google` require JWT authentication
2. **Admin Endpoints**: Endpoints under `/admin` require Admin role
3. **Date Format**: Use ISO 8601 format (YYYY-MM-DD) for dates
4. **Time Format**: Use HH:MM format for times
5. **Pagination**: Most list endpoints support pagination with `page` and `per_page` parameters
6. **Filtering**: Many endpoints support filtering via query parameters
7. **File Uploads**: File uploads use multipart/form-data encoding
8. **Rate Limiting**: API may implement rate limiting for security

---

# 🔄 Recent Updates

- **2024-09-18**: Updated admin endpoints, removed rates management from frontend
- **2024-09-18**: Added comprehensive cost analytics endpoints
- **2024-09-18**: Enhanced leave management with attachment support
- **2024-09-18**: Added employee license management endpoints
- **2024-09-18**: Updated authentication flow documentation

This documentation reflects the current state of the API as of September 2024.