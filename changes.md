# Project Changes & Testing Guide

This document summarizes all the changes and new features implemented in the application.

## Phase 1: Backend Foundation & Bug Fixes

### 1. Timesheet Generation Fix
*   **Change:** Timesheets are now generated automatically when a shift is approved by a manager.
*   **Testing:**
    1.  As a manager, go to the "Shift Roster" page.
    2.  Find a shift with a "pending" status.
    3.  Approve the shift.
    4.  Navigate to the "Timesheets" page. A new timesheet corresponding to the approved shift should now be visible.

### 2. License Management Backend
*   **Change:** The backend now has a full suite of API endpoints to create, read, update, and delete license types, and to assign/unassign them from employees.
*   **Testing:** This is a backend feature. Its functionality will be tested via the frontend in Phase 2.

### 3. Leave Management Backend
*   **Change:** The backend now has API endpoints to handle leave requests (creation, approval, rejection, deletion).
*   **Testing:** This is a backend feature. Its functionality will be tested via the frontend in Phase 2.

### 4. Color-Coded Responsible Areas
*   **Change:** The "Areas of Responsibility" model in the database now has a `color` attribute. The API has been updated to support this.
*   **Testing:** This is a backend feature. Its functionality will be tested via the frontend in Phase 2.

## Phase 2: Frontend Implementation & UI/UX

### 5. License Management UI
*   **Change:** A new "Licenses" tab has been added to the "Admin Panel".
*   **Testing:**
    1.  Log in as an Admin and go to the "Admin Panel".
    2.  Click on the "Licenses" tab.
    3.  You should be able to add a new license type (e.g., "First Aid Certified").
    4.  You should be able to edit and delete existing licenses.

### 6. Leave Request Form & Page
*   **Change:** A new "Leave" page is now available in the sidebar.
*   **Testing:**
    1.  Log in as an **Employee**. Navigate to the "Leave" page. You should see a button to "Request Leave". Fill out and submit the form. Your request should appear in the table with "Pending" status.
    2.  Log out and log in as a **Manager**. Navigate to the "Leave" page. You should see the employee's pending request. You should be able to "Approve" or "Reject" it.

### 7. Employee Form UI Improvements
*   **Change:** The "Add/Edit Employee" form (on the "Employees" page) now has a vertical scrollbar for smaller screens and collapsible accordion sections for Skills, Licenses, and Rates.
*   **Testing:**
    1.  Go to the "Employees" page.
    2.  Click "Add Employee" or edit an existing one.
    3.  Verify that the form is now easier to navigate, with collapsible sections. If the form is long, a scrollbar should appear.

### 8. Area of Responsibility Color UI
*   **Change:** Colors for Areas of Responsibility are now visible in the UI.
*   **Testing:**
    1.  Go to the "Admin Panel" -> "Areas" tab.
    2.  Edit an area and select a color for it using the new color picker input.
    3.  Save the change.
    4.  Go to the "Employees" page. The table should now show the area for each employee as a colored badge.

## Phase 3: New Features & Reports

### 9. Real-time Activity Dashboard
*   **Change:** The "Recent Activity" feed on the Dashboard now shows the latest real actions from the system instead of dummy data.
*   **Testing:**
    1.  As a manager, approve a shift or perform another action.
    2.  Navigate to the "Dashboard".
    3.  The action you just performed should appear at the top of the "Recent Activity" list.

### 10. Advanced Employee Report
*   **Change:** A new "Advanced Employee Report" has been added to the "Reports" page.
*   **Testing:**
    1.  Navigate to the "Reports" page.
    2.  Use the various filter checkboxes (e.g., select a Skill and a Role).
    3.  Click "Search". The table below should update to show only the employees who match all selected criteria, along with their current availability status.

### 11. Employee History Report
*   **Change:** A new "Employee History Report" section has been added to the "Reports" page.
*   **Testing:**
    1.  Navigate to the "Reports" page.
    2.  In the new history report section, select an employee from the dropdown.
    3.  Click "View History". A table should appear showing all the past shifts for that employee.

### 12. Shift Sharing (WhatsApp & Email)
*   **Change:** The "Traditional View" on the "Shift Roster" page now has sharing capabilities.
*   **Testing:**
    1.  Go to the "Shift Roster" and select the "Traditional View" tab.
    2.  On any shift card, click the WhatsApp or Email icon to test single-shift sharing.
    3.  Use the checkboxes to select multiple shifts. A new "Bulk Actions" bar should appear.
    4.  Test the "Copy for WhatsApp" and "Email Selected" buttons.

## Phase 4 & 5: New Features

### 13. Enhanced Exporting
*   **Change:** New export options have been added.
*   **Testing:**
    1.  On the "Shift Roster" -> "Drag & Drop" view, click the "Export Grid" button to download an Excel file that matches the grid layout.
    2.  On the "Timesheets" page, use the new "Export to Excel" button.
    3.  On any row in the timesheet table, test the individual PDF download and Email summary buttons.

### 14. Community Board
*   **Change:** A new "Community" page has been added.
*   **Testing:**
    1.  Navigate to the "Community" page.
    2.  Create a new post.
    3.  Click on your post to view its details, then add a reply.
    4.  Log in as an Admin/Manager and verify you can create a post as an "Announcement".

### 15. WhatsApp Support
*   **Change:** A "Support" link has been added to the sidebar.
*   **Testing:**
    1.  Click the "Support" link in the sidebar.
    2.  It should open a new tab to a WhatsApp chat with a pre-filled message. (Note: The phone number is a placeholder and will need to be configured).
