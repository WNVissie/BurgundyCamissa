from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from datetime import date as date_cls, timedelta

db = SQLAlchemy()

# Designation table for employee designations
class Designation(db.Model):
    __tablename__ = 'designations'
    designation_id = db.Column(db.Integer, primary_key=True)
    designation_name = db.Column(db.String(100), unique=True, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', backref='designation_ref', lazy=True)
    
    def __repr__(self):
        return f'<Designation {self.designation_name}>'
    
    def to_dict(self):
        return {
            'designation_id': self.designation_id,
            'designation_name': self.designation_name,
            'created_on': self.created_on.isoformat() if self.created_on else None
        }

# Association table for many-to-many relationship between employees and skills
employee_skills = db.Table('employee_skills',
    db.Column('employee_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'), primary_key=True),
    db.Column('proficiency_level', db.String(20), default='Beginner'),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    permissions = db.Column(db.Text)  # JSON string for permissions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='role_ref', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def to_dict(self):
        # permissions can be stored as JSON string (expected) or dict (legacy). Normalize to dict.
        perms = {}
        try:
            if isinstance(self.permissions, str):
                perms = json.loads(self.permissions) if self.permissions else {}
            elif isinstance(self.permissions, dict):
                perms = self.permissions
        except Exception:
            perms = {}
        return {
            'id': self.id,
            'name': self.name,
            'permissions': perms,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AreaOfResponsibility(db.Model):
    __tablename__ = 'areas_of_responsibility'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#808080') # Default grey color
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='area_ref', lazy=True)
    
    def __repr__(self):
        return f'<AreaOfResponsibility {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Skill {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class License(db.Model):
    __tablename__ = 'licenses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<License {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Notification model for admin alerts (community posts, approvals, etc.)
class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # recipient (admin)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'community_post', 'timesheet', 'roster', 'leave'
    ref_id = db.Column(db.Integer)  # reference to related object (e.g., post_id)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications', lazy=True)

    def __repr__(self):
        return f'<Notification {self.type} for user {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'ref_id': self.ref_id,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class EmployeeLicense(db.Model):
    __tablename__ = 'employee_licenses'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    license_id = db.Column(db.Integer, db.ForeignKey('licenses.id'), nullable=False)
    expiry_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    license = db.relationship('License', backref='employee_assoc', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)  # Made nullable for username/password users
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=True)  # New field for username login
    password_hash = db.Column(db.String(255), nullable=True)  # New field for password hash
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(50), unique=True, nullable=True)
    contact_no = db.Column(db.String(20), nullable=False, default='')
    alt_contact_name = db.Column(db.String(100))
    alt_contact_no = db.Column(db.String(20))
    designation_id = db.Column(db.Integer, db.ForeignKey('designations.designation_id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    area_of_responsibility_id = db.Column(db.Integer, db.ForeignKey('areas_of_responsibility.id'))
    rate_type = db.Column(db.String(50), name='rate_type')
    rate_value = db.Column(db.Numeric(10, 2), name='rate_-value')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_no_leave_days_annual = db.Column(db.Float)  # Annual leave allocation set by admin
    total_no_leave_days_annual_float = db.Column(db.Float)   # Remaining leave days (updated when leave is approved)
    
    # Relationships
    skills = db.relationship('Skill', secondary=employee_skills, lazy='subquery',
                           backref=db.backref('employees', lazy=True))
    shift_rosters = db.relationship('ShiftRoster', foreign_keys='ShiftRoster.employee_id', backref='employee', lazy=True)
    timesheets = db.relationship('Timesheet', foreign_keys='Timesheet.employee_id', backref='employee', lazy=True)
    approved_rosters = db.relationship('ShiftRoster', foreign_keys='ShiftRoster.approved_by', backref='approver', lazy=True)
    approved_timesheets = db.relationship('Timesheet', foreign_keys='Timesheet.approved_by', backref='timesheet_approver', lazy=True)
    licenses_assoc = db.relationship('EmployeeLicense', backref='employee', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.name} {self.surname}>'
    
    def to_dict(self, include_rates=True):
        licenses_detailed = []
        today = date_cls.today()
        for assoc in self.licenses_assoc or []:
            exp = assoc.expiry_date
            days_to_expiry = (exp - today).days if exp else None
            licenses_detailed.append({
                'license': assoc.license.to_dict() if assoc.license else None,
                'license_id': assoc.license_id,
                'expiry_date': exp.isoformat() if exp else None,
                'days_to_expiry': days_to_expiry,
                'expired': days_to_expiry is not None and days_to_expiry < 0,
                'expiring_soon': days_to_expiry is not None and days_to_expiry <= 30
            })

        result = {
            'id': self.id,
            'google_id': self.google_id,
            'email': self.email,
            'username': self.username,
            'name': self.name,
            'surname': self.surname,
            'employee_id': self.employee_id,
            'contact_no': self.contact_no,
            'alt_contact_name': self.alt_contact_name,
            'alt_contact_no': self.alt_contact_no,
            'licenses_detailed': licenses_detailed,
            'designation': self.designation_ref.designation_name if self.designation_ref else None,
            'role_id': self.role_id,
            'role': self.role_ref.to_dict() if self.role_ref else None,
            'area_of_responsibility_id': self.area_of_responsibility_id,
            'area_of_responsibility': self.area_ref.to_dict() if self.area_ref else None,
            'skills': [skill.to_dict() for skill in self.skills],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_no_leave_days_annual': float(self.total_no_leave_days_annual) if self.total_no_leave_days_annual is not None else None,
            'total_no_leave_days_annual_float': float(self.total_no_leave_days_annual_float) if self.total_no_leave_days_annual_float is not None else None
        }
        
        # Only include rate information if explicitly requested (for admin users)
        if include_rates:
            result['rate_type'] = self.rate_type
            result['rate_value'] = float(self.rate_value) if self.rate_value is not None else None
            
        return result

class Shift(db.Model):
    __tablename__ = 'shifts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#3498db')  # Hex color for UI
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    shift_rosters = db.relationship('ShiftRoster', backref='shift', lazy=True)
    
    def __repr__(self):
        return f'<Shift {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'hours': self.hours,
            'description': self.description,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ShiftRoster(db.Model):
    __tablename__ = 'shift_roster'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shift_id = db.Column(db.Integer, db.ForeignKey('shifts.id'), nullable=False)
    area_of_responsibility_id = db.Column(db.Integer, db.ForeignKey('areas_of_responsibility.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, accepted
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    accepted_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    timesheets = db.relationship('Timesheet', backref='roster', lazy=True)
    area = db.relationship('AreaOfResponsibility', backref='shift_rosters', lazy=True)
    
    def __repr__(self):
        return f'<ShiftRoster {self.employee.name} - {self.shift.name} - {self.date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee': {
                'id': self.employee.id,
                'name': self.employee.name,
                'surname': self.employee.surname,
                'employee_id': self.employee.employee_id,
                'role': self.employee.role_ref.name if self.employee.role_ref else None,
                'area': self.employee.area_ref.name if self.employee.area_ref else None
            } if self.employee else None,
            'shift_id': self.shift_id,
            'shift': self.shift.to_dict() if self.shift else None,
            'area_of_responsibility_id': self.area_of_responsibility_id,
            'area': self.area.to_dict() if self.area else None,
            'date': self.date.isoformat() if self.date else None,
            'hours': self.hours,
            'status': self.status,
            'approved_by': self.approved_by,
            'approver': {
                'id': self.approver.id,
                'name': self.approver.name,
                'surname': self.approver.surname
            } if self.approver else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'timesheet': self.timesheets[0].to_dict() if self.timesheets else None
        }

class Timesheet(db.Model):
    __tablename__ = 'timesheets'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    roster_id = db.Column(db.Integer, db.ForeignKey('shift_roster.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours_worked = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    accepted_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Timesheet {self.employee.name} - {self.date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee': {
                'id': self.employee.id,
                'name': self.employee.name,
                'surname': self.employee.surname,
                'employee_id': self.employee.employee_id
            } if self.employee else None,
            'roster_id': self.roster_id,
            'date': self.date.isoformat() if self.date else None,
            'hours_worked': self.hours_worked,
            'status': self.status,
            'approved_by': self.approved_by,
            'approver': {
                'id': self.timesheet_approver.id,
                'name': self.timesheet_approver.name,
                'surname': self.timesheet_approver.surname
            } if self.timesheet_approver else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None
        }

class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    leave_type = db.Column(db.String(20), nullable=False)  # paid, unpaid, sick
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days = db.Column(db.Numeric)  # Change to Numeric if partial days allowed
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    action_comment = db.Column(db.String(255))  # <-- Add this line
    no_of_leave_days_remaining = db.Column(db.Numeric)
    authorised_by = db.Column(db.Integer)
    authorised_at = db.Column(db.DateTime)
    
    # Attachment fields for supporting documents
    attachment_filename = db.Column(db.String(255))  # Original filename
    attachment_path = db.Column(db.String(500))      # Server file path
    attachment_mimetype = db.Column(db.String(100))  # File MIME type
    attachment_size = db.Column(db.Integer)          # File size in bytes
    attachment_uploaded_at = db.Column(db.DateTime)  # Upload timestamp

    # Relationships
    employee = db.relationship('User', foreign_keys=[employee_id], backref='leave_requests')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_leaves')

    def __repr__(self):
        return f'<LeaveRequest {self.employee.name} - {self.leave_type} - {self.start_date}>'
    
    def to_dict(self):
        # Get authorised_by user name if exists
        authorised_by_name = None
        if self.authorised_by:
            authoriser = User.query.get(self.authorised_by)
            if authoriser:
                authorised_by_name = f"{authoriser.name} {authoriser.surname}"
        
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee': {
                'id': self.employee.id,
                'name': self.employee.name,
                'surname': self.employee.surname,
                'employee_id': self.employee.employee_id
            } if self.employee else None,
            'leave_type': self.leave_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'days': float(self.days) if self.days is not None else 0,
            'reason': self.reason,
            'status': self.status,
            'approved_by': self.approved_by,
            'approver': {
                'id': self.approver.id,
                'name': self.approver.name,
                'surname': self.approver.surname
            } if self.approver else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'action_comment': self.action_comment,
            'no_of_leave_days_remaining': float(self.no_of_leave_days_remaining) if self.no_of_leave_days_remaining is not None else 0,
            'authorised_by': self.authorised_by,
            'authorised_by_name': authorised_by_name,
            'authorised_at': self.authorised_at.isoformat() if self.authorised_at else None,
            'total_no_leave_days_annual': float(self.employee.total_no_leave_days_annual) if self.employee and self.employee.total_no_leave_days_annual is not None else None,
            # Attachment information
            'has_attachment': bool(self.attachment_filename),
            'attachment': {
                'filename': self.attachment_filename,
                'mimetype': self.attachment_mimetype,
                'size': self.attachment_size,
                'uploaded_at': self.attachment_uploaded_at.isoformat() if self.attachment_uploaded_at else None
            } if self.attachment_filename else None
        }

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='activities')

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.name + ' ' + self.user.surname if self.user else 'Unknown User',
            'action': self.action,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

class CommunityPost(db.Model):
    __tablename__ = 'community_posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_type = db.Column(db.String(50), default='Question') # 'Question' or 'Announcement'
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='community_posts')
    replies = db.relationship('PostReply', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'author': self.author.to_dict() if self.author else None,
            'post_type': self.post_type,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'reply_count': self.replies.count()
        }

class PostReply(db.Model):
    __tablename__ = 'post_replies'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('community_posts.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='post_replies')

    def to_dict(self):
        return {
            'id': self.id,
            'author': self.author.to_dict() if self.author else None,
            'post_id': self.post_id,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }

class EmployeeRate(db.Model):
    __tablename__ = 'employee_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rate_type = db.Column(db.String(20), nullable=False)  # 'hourly', 'daily', 'weekly', 'monthly'
    rate_value = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='ZAR')  # Currency code
    effective_date = db.Column(db.Date, nullable=False)  # When this rate becomes effective
    end_date = db.Column(db.Date, nullable=True)  # When this rate expires (NULL = current)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)  # Optional notes about the rate
    
    # Relationships
    employee = db.relationship('User', foreign_keys=[employee_id], backref='employee_rates')
    created_by_user = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<EmployeeRate {self.employee_id}: {self.rate_type} {self.rate_value}>'
    
    def to_dict(self, include_sensitive=False):
        result = {
            'id': self.id,
            'employee_id': self.employee_id,
            'rate_type': self.rate_type,
            'currency': self.currency,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'notes': self.notes
        }
        
        # Only include rate_value for admin users or the employee themselves
        if include_sensitive:
            result['rate_value'] = float(self.rate_value) if self.rate_value else None
            
        return result
    
    @staticmethod
    def get_current_rate(employee_id, rate_type=None):
        """Get the current active rate for an employee"""
        today = date_cls.today()
        query = EmployeeRate.query.filter(
            EmployeeRate.employee_id == employee_id,
            EmployeeRate.effective_date <= today,
            (EmployeeRate.end_date == None) | (EmployeeRate.end_date > today)
        )
        
        if rate_type:
            query = query.filter(EmployeeRate.rate_type == rate_type)
            
        return query.order_by(EmployeeRate.effective_date.desc()).first()
    
    def calculate_cost_for_hours(self, hours_worked):
        """Calculate cost based on rate type and hours worked"""
        if not self.rate_value or not hours_worked:
            return 0
        
        rate = float(self.rate_value)
        
        if self.rate_type == 'hourly':
            return hours_worked * rate
        elif self.rate_type == 'daily':
            # Assume 8 hours per day
            days = hours_worked / 8
            return days * rate
        elif self.rate_type == 'weekly':
            # Assume 40 hours per week
            weeks = hours_worked / 40
            return weeks * rate
        elif self.rate_type == 'monthly':
            # Assume 160 hours per month (4 weeks * 40 hours)
            months = hours_worked / 160
            return months * rate
        else:
            # Default to hourly if unknown type
            return hours_worked * rate


class HourlyRates(db.Model):
    """Simplified hourly rates table - focuses only on hourly rates"""
    __tablename__ = 'hourly_rates'
    
    # Primary Key
    rate_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key to link to employees (users table)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Hourly rate - use Numeric for precise currency calculations
    rate_per_hr = db.Column(db.Numeric(10, 2), nullable=False)  # e.g., 125.50
    
    # Currency (defaults to ZAR)
    currency = db.Column(db.String(3), default='ZAR', nullable=False)
    
    # When this rate becomes effective
    effective_date = db.Column(db.Date, nullable=False, default=date_cls.today)
    
    # When this rate expires (NULL means current)
    end_date = db.Column(db.Date, nullable=True)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    employee = db.relationship('User', foreign_keys=[employee_id], backref='hourly_rates')
    created_by_user = db.relationship('User', foreign_keys=[created_by])
    
    # Indexes for performance
    __table_args__ = (
        db.Index('ix_hourly_rates_employee_effective', 'employee_id', 'effective_date'),
        db.Index('ix_hourly_rates_active', 'employee_id', 'effective_date', 'end_date'),
    )
    
    def __repr__(self):
        return f'<HourlyRate {self.employee_id}: R{self.rate_per_hr}/hr>'
    
    def to_dict(self, include_rate=True):
        result = {
            'rate_id': self.rate_id,
            'employee_id': self.employee_id,
            'currency': self.currency,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Only include rate for authorized users
        if include_rate:
            result['rate_per_hr'] = float(self.rate_per_hr) if self.rate_per_hr else None
            
        return result
    
    @staticmethod
    def get_current_rate(employee_id):
        """Get the current active hourly rate for an employee"""
        today = date_cls.today()
        
        return HourlyRates.query.filter(
            HourlyRates.employee_id == employee_id,
            HourlyRates.effective_date <= today,
            (HourlyRates.end_date == None) | (HourlyRates.end_date > today)
        ).order_by(HourlyRates.effective_date.desc()).first()
    
    def calculate_cost(self, hours_worked):
        """Calculate total cost for hours worked"""
        if not self.rate_per_hr or not hours_worked:
            return 0
        return float(self.rate_per_hr) * hours_worked
