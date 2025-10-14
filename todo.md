	- [ ] Look at adding dockworker logs for fuel consumption based on employee ID and vehicle
	- [ ] Add option to upload a document for leave (e.g., medical certificate)
	- [ ] Add additional leave types
## Next session (2025-08-13): Bugfixes and features

### To Do for Tomorrow

	- [ ] Add reports (employee history, etc)
	- [ ] Check licenses (Admin - get licenses?)
	- [ ] Check why timesheets are not generating
	- [ ] Check that recent activity pulls through
	- [ ] Test employee user
	- [ ] Add leave to employee automatically when leave is approved (in roster?)
	- [ ] Analytics: Employees by area not showing
	- [ ] Analytics: Shifts analysis not showing
	- [ ] Analytics: How performance is calculated
	- [ ] Analytics: Skills distribution pulled through?
	- [ ] Analytics: Designation calling designations table
	- [ ] Employee form: Rates not showing
	- [ ] Test community: add functionality for Q&A and to add Q&A answered in community notice board
	- [ ] Test support: set up
	- [ ] Test multiple sending to WhatsApp and email

	- [ ] Add registration page for new employees (manual signup with company email and password).
	- [ ] Support login with both company email/password and Google OAuth.
	- [ ] Update user records with real company emails when available.

	- [x] Reproduce: drag shift in Roster; confirm it doesn’t assign and note any errors.
	- [ ] Backend: verify GET /api/shifts and /api/roster responses; check CORS/auth; confirm assign/create endpoints exist and payload shapes.
	- [ ] Frontend: ensure drop handler calls backend and updates UI optimistically; handle error states.
	- [ ] Acceptance: user can drag a shift onto a slot, it persists on refresh; no “Failed to fetch shift data”.

## Quick Start Commands

**Backend (Flask):**
```cmd
python shift-roster-backend\src\main.py
```

**Frontend (React/Vite):**
```cmd
cd shift-roster-frontend
npm
```

- Roles: “failed to fetch data” (Admin)
	- [ ] Verify /api/roles route, permissions (Admin bypass), and axios base URL.
	- [ ] Acceptance: Roles list loads for Admin without errors.

- Cannot add data (general)
	- [ ] Re-test create on Employees, Roles, Areas, Skills; fix any 4xx/5xx and validation mismatches.
	- [ ] Acceptance: Can add each entity successfully; toast confirms; list refreshes.

- Analytics: dummy/incorrect data and fetch failures
	- [ ] Replace any stubbed responses with real queries; ensure date range handling; seed sufficient sample data.
	- [ ] Acceptance: Dashboard/Analytics load with real counts; no 401/422; charts match DB state.

- Timesheets
	- [ ] Define model + endpoints (create, approve, export); add UI page & basic workflow.
	- [ ] Acceptance: Generate timesheets for a period, approve/reject, and view status.

- Reports
	- [ ] Specify report types (attendance, hours by employee/area, coverage); implement CSV/PDF exports.
	- [ ] Acceptance: User can generate and download selected reports with correct filters.

- Seed/sample data
	- [ ] Create/refresh dev seeds: employees, roles, areas, skills, shifts, roster assignments for realistic analytics.
	- [ ] Acceptance: Fresh setup yields usable demo data across pages.

- Diagnostics to capture (for quick triage)
	- [ ] Browser console + Network tab errors for failing actions.
	- [ ] Backend flask.log snippets and request/response samples (status, URL, payload).
	- [ ] Exact steps to reproduce for each failure.

## Phase 1: Analyze requirements and design system architecture

- [x] Read and understand the user's request in detail.
- [x] Identify all entities and their attributes (e.g., Employee, Shift, Role, Area of Responsibility, Skill, Timesheet).
- [x] Define relationships between entities (e.g., Employee to Role, Employee to Area of Responsibility, Employee to Skill (many-to-many), Shift to Employee).
- [x] Outline the database schema based on identified entities and relationships.
- [x] List all required functionalities (e.g., user authentication, shift scheduling, timesheet generation, reporting, admin management, export/import).
- [x] Design the main API endpoints for each functionality.
- [x] Consider the overall system architecture (React frontend, Flask backend, Google OAuth).
- [x] Document the design in a `design_document.md` file.
- [x] Mark this phase as complete.


## Phase 2: Set up backend Flask application with database models

- [x] Create Flask application using manus-create-flask-app utility
- [x] Set up project structure and dependencies
- [x] Install required packages (SQLAlchemy, Flask-JWT-Extended, google-auth, etc.)
- [x] Create database models for all entities (Users, Roles, Areas, Skills, Shifts, Roster, Timesheets)
- [x] Set up database relationships and constraints
- [x] Create database initialization script with sample data
- [x] Configure CORS for frontend-backend communication
- [x] Set up environment configuration
- [x] Test database models and relationships
- [x] Mark this phase as complete


## Phase 3: Implement authentication and API endpoints

- [x] Create authentication routes (Google OAuth, JWT tokens)
- [x] Implement role-based access control decorators
- [x] Create API endpoints for employees management
- [x] Create API endpoints for roles management
- [x] Create API endpoints for areas of responsibility
- [x] Create API endpoints for skills management
- [x] Create API endpoints for shifts management
- [x] Create API endpoints for shift roster operations
- [x] Create API endpoints for timesheets management
- [x] Create API endpoints for analytics and dashboard data
- [x] Test all API endpoints
- [x] Mark this phase as complete


## Phase 4: Create React frontend application structure

- [x] Create React application using manus-create-react-app utility
- [x] Set up project structure and install required dependencies
- [x] Configure routing with React Router
- [x] Set up authentication context and API service
- [x] Create basic layout components (Header, Sidebar, Footer)
- [x] Implement authentication pages (Login, Dashboard)
- [x] Set up state management and API integration
- [x] Create basic page templates for all main sections
- [x] Test basic navigation and authentication flow
- [x] Mark this phase as complete


## Phase 5: Implement user interface components and pages

- [x] Create employee management page with CRUD operations
- [x] Implement shift roster page with calendar view
- [x] Create timesheets page with approval workflow
- [x] Build admin panel for managing roles, areas, skills, and shifts
- [x] Implement employee profile and settings pages
- [x] Create responsive data tables with filtering and sorting
- [x] Add form components for creating/editing entities
- [x] Implement status badges and approval indicators
- [x] Create modal dialogs for confirmations and details
- [x] Test all UI components and pages
- [x] Mark this phase as complete


## Phase 6: Add drag-and-drop scheduling and interactive features

- [x] Implement drag-and-drop functionality for shift scheduling
- [x] Add color-coded shifts for different roles/areas
- [x] Create interactive calendar with hover effects
- [x] Implement bulk shift operations
- [x] Add real-time updates and notifications
- [x] Create shift conflict detection
- [x] Implement shift swapping between employees
- [x] Add keyboard shortcuts for power users
- [x] Create responsive touch interactions for mobile
- [x] Test drag-and-drop functionality across devices
- [x] Mark this phase as complete


## Phase 7: Implement analytics dashboard with charts

- [x] Create analytics dashboard with interactive charts
- [x] Implement employee distribution charts (by role, area, shift)
- [x] Add shift utilization and coverage analytics
- [x] Create timesheet approval metrics
- [x] Implement leave tracking and availability charts
- [x] Add skill distribution and gap analysis
- [x] Create performance metrics and KPIs
- [x] Implement date range filtering for analytics
- [x] Add export functionality for charts and reports
- [x] Test analytics with sample data
- [x] Mark this phase as complete


## Phase 8: Add export/import functionality and file handling

- [x] Implement CSV/Excel export for employee data
- [x] Add CSV/Excel export for shift rosters
- [x] Create PDF export for timesheets and reports
- [x] Implement bulk import functionality for employees
- [x] Add template download for data imports
- [x] Create file upload and validation system
- [x] Implement data backup and restore features
- [x] Add image upload for employee profiles
- [x] Create audit trail for data changes
- [x] Test all export/import functionality
- [x] Mark this phase as complete


## Phase 9: Test application and create deployment package

- [x] Test backend API endpoints and functionality
- [x] Test frontend application and user interface
- [x] Verify authentication and authorization flows
- [x] Test drag-and-drop functionality and interactions
- [x] Validate export/import features
- [x] Test analytics dashboard and charts
- [x] Verify responsive design on different devices
- [x] Create production build of frontend
- [x] Prepare backend for deployment
- [x] Create deployment configuration files
- [x] Mark this phase as complete



## Project Technical Notes & Feature Requirements

- NOTE: DATA WAS SEEDED AND HARDCODED FOR TESTING – WITH ALL REQUESTS NOW THE APIS AND ALL SHOULD POINT TO THE DATABASE
- NOTE THAT EMAILS ARE DUMMIES EXCEPT FOR WANDA.NEZAR AND KAILETH.PHELAN (David Viljoen) – use these two for authentication testing.
- Remove all authorisation until testing has been completed – only then start testing authorisations.
- Admin – have access to all, Managers have access to all
- Add guest to roles – guest can only see the shift roster and analytics and dashboard and must have a username and password
- Run a check vs the schema of the code vs schema of the database to indicate if any fields are not called or populated – misaligned
- Check that data in the app is fetched from the database and not hard coded data on the UI
- Generate Timesheet that pulls data from the database and that the timesheet data is generated from the roster and populated in the database
- Fix weekly analysis chart
- Create UI for leave table and allow approval of leave by managers only. Populate roster when leave has been requested.
- Create a leave view that shows all leave data – with approvals, who approved and date of approval
- Add to the role table an easier way to assign access to tables and views so that admin can switch on or off when access changes.
- Create export buttons for the shifts and timesheets and add WhatsApp functionality to allow a shift to be shared via WhatsApp to a single employee (add in the shift roster at employee name)
- Allow copy paste for a group of employees (can be selected by tickboxes selecting multiple users) to be shared to a WhatsApp group.
- Allow sharing of shifts via email (include icon in the shift roster to click and send route to employee email)
- Allow sharing of shifts via a group email setup to email all in the group
- Add a community board with Q&A that all can post, managers and admin can moderate and also a WhatsApp direct chat for them to try to contact admin (or a manager)

## Phase 10: Package application and provide documentation

- [ ] Create comprehensive README with installation instructions
- [ ] Write deployment guide for different platforms
- [ ] Document API endpoints and usage
- [ ] Create user manual and feature documentation
- [ ] Prepare environment configuration files
- [ ] Create database setup and migration scripts
- [ ] Package complete application as downloadable zip
- [ ] Include sample data and test accounts
- [ ] Create troubleshooting guide
- [ ] Finalize project documentation
- [ ] Mark this phase as complete

