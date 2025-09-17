# Employee Shift Roster Application - Design Document

## Overview
A comprehensive employee shift roster application with React frontend and Flask backend, featuring Google authentication, role-based access control, shift management, timesheets, and analytics.

## System Architecture

### Frontend (React)
- React application with modern UI components
- Google OAuth integration for authentication
- Drag-and-drop scheduling interface
- Interactive charts and dashboards
- Responsive design for desktop and mobile
- Export/import functionality

### Backend (Flask)
- RESTful API with Flask
- SQLAlchemy ORM for database operations
- Google OAuth verification
- JWT token-based authentication
- File upload/download handling
- Data export to Excel/PDF

### Database Schema

#### Users Table
- id (Primary Key)
- google_id (Unique, String)
- email (Unique, String)
- name (String)
- surname (String)
- employee_id (Unique, String, nullable)
- contact_no (String, default='')
- alt_contact_name (String, nullable)
- alt_contact_no (String, nullable)
- designation_id (Foreign Key to Designations)
- role_id (Foreign Key to Roles, not null)
- area_of_responsibility_id (Foreign Key to Areas)
- created_at (DateTime)
- updated_at (DateTime)
- Relationships:
	- skills (Many-to-Many with Skills)
	- shift_rosters (One-to-Many with ShiftRoster)
	- timesheets (One-to-Many with Timesheet)
	- approved_rosters (One-to-Many with ShiftRoster, as approver)
	- approved_timesheets (One-to-Many with Timesheet, as approver)
	- licenses_assoc (One-to-Many with EmployeeLicense)

#### Roles Table
- id (Primary Key)
- name (Unique, String)
- permissions (JSON/Text)
- created_at (DateTime)
- Relationships:
	- users (One-to-Many with Users)

#### Designations Table
- designation_id (Primary Key)
- designation_name (Unique, String)
- created_on (DateTime)
- Relationships:
	- users (One-to-Many with Users)

#### Areas of Responsibility Table
- id (Primary Key)
- name (Unique, String)
- description (Text)
- created_at (DateTime)
- Relationships:
	- users (One-to-Many with Users)

#### Skills Table
- id (Primary Key)
- name (Unique, String)
- description (Text)
- created_at (DateTime)
- Relationships:
	- employees (Many-to-Many with Users)

#### Employee Skills Table (Many-to-Many)
- employee_id (Foreign Key to Users)
- skill_id (Foreign Key to Skills)
- proficiency_level (String, default='Beginner')
- created_at (DateTime)

#### Licenses Table
- id (Primary Key)
- name (Unique, String)
- description (Text)
- created_at (DateTime)

#### Employee Licenses Table
- id (Primary Key)
- employee_id (Foreign Key to Users)
- license_id (Foreign Key to Licenses)
- expiry_date (Date)
- created_at (DateTime)

#### Shifts Table
- id (Primary Key)
- name (Unique, String)
- start_time (Time)
- end_time (Time)
- hours (Float)
- description (Text)
- color (String, default='#3498db')
- created_at (DateTime)
- Relationships:
	- shift_rosters (One-to-Many with ShiftRoster)

#### Shift Roster Table
- id (Primary Key)
- employee_id (Foreign Key to Users, not null)
- shift_id (Foreign Key to Shifts, not null)
- date (Date)
- hours (Float)
- status (String, default='pending')
- approved_by (Foreign Key to Users)
- approved_at (DateTime)
- notes (Text)
- created_at (DateTime)
- Relationships:
	- timesheets (One-to-Many with Timesheet)

#### Timesheets Table
- id (Primary Key)
- employee_id (Foreign Key to Users, not null)
- roster_id (Foreign Key to ShiftRoster, not null)
- date (Date)
- hours_worked (Float)
- status (String, default='pending')
- approved_by (Foreign Key to Users)
- approved_at (DateTime)
- notes (Text)
- created_at (DateTime)

#### Leave Requests Table
- id (Primary Key)
- employee_id (Foreign Key to Users, not null)
- leave_type (String: paid, unpaid, sick)
- start_date (Date)
- end_date (Date)
- days (Integer)
- reason (Text)
- status (String, default='pending')
- approved_by (Foreign Key to Users)
- approved_at (DateTime)
- created_at (DateTime)


## Key Features

### Authentication & Authorization
- Google OAuth 2.0 integration
- Role-based access control (Admin, Manager, Employee, Guest)
- JWT token management

### Admin Management
- Employee management (CRUD operations)
- Role management
- Skills management
- Area of responsibility management
- Shift type management

### Shift Scheduling
- Drag-and-drop interface for scheduling
- Color-coded shifts
- Date range picker
- Bulk scheduling operations
- Approval workflow

### Timesheets
- Auto-generation from approved shift rosters
- Manager approval workflow
- Time tracking and reporting

### Analytics Dashboard
- Employee count by shift, role, area
- Target vs actual metrics
- Leave tracking (paid, unpaid, sick)
- Skill-based employee search
- Interactive charts and visualizations

### Export/Import
- Template downloads for all tables
- Bulk data upload via templates
- Excel export for rosters and timesheets
- PDF export for reports

## API Endpoints

### Authentication
- POST /api/auth/google - Google OAuth login
- POST /api/auth/refresh - Refresh JWT token
- POST /api/auth/logout - Logout user

### Users/Employees
- GET /api/employees - List all employees
- POST /api/employees - Create employee
- GET /api/employees/{id} - Get employee details
- PUT /api/employees/{id} - Update employee
- DELETE /api/employees/{id} - Delete employee

### Roles
- GET /api/roles - List all roles
- POST /api/roles - Create role
- PUT /api/roles/{id} - Update role
- DELETE /api/roles/{id} - Delete role

### Areas of Responsibility
- GET /api/areas - List all areas
- POST /api/areas - Create area
- PUT /api/areas/{id} - Update area
- DELETE /api/areas/{id} - Delete area

### Skills
- GET /api/skills - List all skills
- POST /api/skills - Create skill
- PUT /api/skills/{id} - Update skill
- DELETE /api/skills/{id} - Delete skill

### Shifts
- GET /api/shifts - List all shift types
- POST /api/shifts - Create shift type
- PUT /api/shifts/{id} - Update shift type
- DELETE /api/shifts/{id} - Delete shift type

### Shift Roster
- GET /api/roster - Get shift roster (with filters)
- POST /api/roster - Create roster entry
- PUT /api/roster/{id} - Update roster entry
- DELETE /api/roster/{id} - Delete roster entry
- POST /api/roster/{id}/approve - Approve roster entry

### Timesheets
- GET /api/timesheets - Get timesheets (with filters)
- POST /api/timesheets/generate - Generate from approved rosters
- PUT /api/timesheets/{id} - Update timesheet
- POST /api/timesheets/{id}/approve - Approve timesheet

### Analytics
- GET /api/analytics/dashboard - Dashboard metrics
- GET /api/analytics/employees-by-shift - Employee count by shift
- GET /api/analytics/employees-by-role - Employee count by role
- GET /api/analytics/employees-by-area - Employee count by area
- GET /api/analytics/leave-summary - Leave summary

### Export/Import
- GET /api/export/template/{table} - Download template
- POST /api/import/{table} - Upload data
- GET /api/export/roster - Export roster to Excel
- GET /api/export/timesheets - Export timesheets to Excel
- GET /api/export/dashboard - Export dashboard to PDF

## Frontend Pages

### Landing Page
- Dashboard overview
- Quick navigation to main sections
- Key metrics cards

### Shift Roster
- Calendar view with drag-and-drop
- Color-coded shifts
- Filter by date range, employee, role
- Approval status indicators

### Admin Panel
- Employee management
- Role management
- Skills management
- Area management
- Shift type management

### Analytics Dashboard
- Interactive charts
- Employee metrics
- Leave tracking
- Skill-based search

### Timesheets
- Timesheet listing
- Approval workflow
- Export functionality

### Reports
- Various report types
- Export options
- Date range filters

## Additional Tables for Future Expansion

Below are tables present in your database schema but not yet fully described in the design document. You can add these to your design for completeness and future development:

---

### Activity Logs Table (used but testing currently)

Tracks user actions and system events for auditing and monitoring.

**Fields:**
- `id` (Primary Key)
- `user_id` (Foreign Key to Users)
- `action` (String, e.g., "Logged in", "Created shift", "Approved leave")
- `timestamp` (DateTime)
- `details` (Text, optional — additional info about the action)

**Relationships:**
- Linked to Users (One-to-Many: one user can have many activity logs)

---

### Community Posts Table (testing)

Allows users to post messages or announcements to the team.

**Fields:**
- `id` (Primary Key)
- `user_id` (Foreign Key to Users)
- `content` (Text)
- `created_at` (DateTime)

**Relationships:**
- Linked to Users (One-to-Many: one user can have many posts)

---

### Areas Table (Reserved for Future Use)

Defines physical or logical areas within the organization.

**Fields:**
- `area_id` (Primary Key)
- `name` (Unique, String)
- `description` (Text, optional)
- `created_at` (DateTime, optional)

**Note:**  
Currently not used in the application, but reserved for future expansion.

---

Add these tables to your design document to keep it aligned with your schema and to support future features such as auditing, team communication,


## Technology Stack

### Frontend
- React 18
- Material-UI or Ant Design
- React Router
- Axios for API calls
- Chart.js or Recharts for analytics
- React DnD for drag-and-drop
- Google OAuth library

### Backend
- Flask
- SQLAlchemy
- Flask-JWT-Extended
- Google Auth Library
- Pandas for data processing
- openpyxl for Excel export
- ReportLab for PDF generation

### Database
- SQLite for development
- PostgreSQL for production

## Security Considerations
- Google OAuth for secure authentication
- JWT tokens with expiration
- Role-based access control
- Input validation and sanitization
- CORS configuration
- Rate limiting on API endpoints

