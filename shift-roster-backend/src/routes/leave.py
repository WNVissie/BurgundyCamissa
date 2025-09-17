from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from src.models.models import db, LeaveRequest, User, Shift, ShiftRoster
from src.utils.decorators import get_current_user, manager_required
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os
import uuid
import hashlib

leave_bp = Blueprint('leave', __name__)

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'leave_attachments')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB (reduced from 5MB)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_leave_attachment(file, leave_request_id):
    """Save uploaded file and return file info."""
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        raise ValueError("File type not allowed")
    
    # Create unique filename to avoid collisions
    original_filename = secure_filename(file.filename)
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"leave_{leave_request_id}_{uuid.uuid4().hex}.{file_extension}"
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Save file
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    return {
        'filename': original_filename,
        'path': file_path,
        'unique_filename': unique_filename,
        'mimetype': file.mimetype,
        'size': file_size
    }

@leave_bp.route('', methods=['GET'])
@jwt_required()
def get_leave_requests():
    """
    Get leave requests.
    - Admins/Managers can see all requests.
    - Employees can only see their own requests.
    """
    try:
        current_user = get_current_user()
        query = LeaveRequest.query

        # Filter by role
        if current_user.role_ref.name not in ['Admin', 'Manager']:
            query = query.filter(LeaveRequest.employee_id == current_user.id)

        # Optional filters
        status = request.args.get('status')
        employee_id = request.args.get('employee_id')

        if status:
            query = query.filter(LeaveRequest.status == status)
        if employee_id and current_user.role_ref.name in ['Admin', 'Manager']:
             query = query.filter(LeaveRequest.employee_id == int(employee_id))

        requests = query.order_by(LeaveRequest.start_date.desc()).all()
        return jsonify([r.to_dict() for r in requests]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leave_bp.route('', methods=['POST'])
@jwt_required()
def create_leave_request():
    """Create a new leave request with optional file attachment."""
    try:
        current_user = get_current_user()
        
        # Handle both form data (with files) and JSON data
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Form data with potential file upload
            data = request.form.to_dict()
            file = request.files.get('attachment')
        else:
            # JSON data without file
            data = request.get_json()
            file = None

        required_fields = ['leave_type', 'start_date', 'end_date', 'reason']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

        if start_date > end_date:
            return jsonify({'error': 'Start date cannot be after end date'}), 400

        days = (end_date - start_date).days + 1
        
        # Calculate remaining days when leave is created
        # Get all authorised leave for this employee
        authorised_leaves = LeaveRequest.query.filter_by(
            employee_id=current_user.id, 
            status='authorised'
        ).all()
        
        total_used_days = sum(float(leave.days) for leave in authorised_leaves)
        annual_leave_allocation = float(current_user.total_no_leave_days_annual or 0)
        
        # Calculate what would remain if this leave is approved
        remaining_days = annual_leave_allocation - total_used_days - days

        new_request = LeaveRequest(
            employee_id=current_user.id,
            leave_type=data['leave_type'],
            start_date=start_date,
            end_date=end_date,
            days=days,
            reason=data['reason'],
            no_of_leave_days_remaining=remaining_days  # Store what would remain if approved
        )
        
        # Add to session to get ID
        db.session.add(new_request)
        db.session.flush()  # This assigns the ID without committing
        
        # Handle file upload if present
        if file and file.filename:
            try:
                # Check file size
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)  # Reset file pointer
                
                if file_size > MAX_FILE_SIZE:
                    return jsonify({'error': 'File size exceeds 5MB limit'}), 400
                
                file_info = save_leave_attachment(file, new_request.id)
                
                # Update leave request with file info
                new_request.attachment_filename = file_info['filename']
                new_request.attachment_path = file_info['path']
                new_request.attachment_mimetype = file_info['mimetype']
                new_request.attachment_size = file_info['size']
                new_request.attachment_uploaded_at = datetime.utcnow()
                
            except ValueError as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': f'File upload failed: {str(e)}'}), 500
        
        db.session.commit()
        return jsonify(new_request.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/<int:request_id>/approve', methods=['POST'])
@jwt_required()
@manager_required
def approve_leave_request(request_id):
    """Supervisor approves a leave request (first stage)."""
    try:
        current_user = get_current_user()
        leave_request = LeaveRequest.query.get(request_id)
        if not leave_request:
            return jsonify({'error': 'Leave request not found'}), 404

        if leave_request.status != 'pending':
            return jsonify({'error': 'Leave request is not in pending status'}), 400

        data = request.get_json()
        action = data.get('action')  # 'approve' or 'reject'

        if action not in ['approve', 'reject']:
            return jsonify({'error': 'Invalid action. Must be "approve" or "reject"'}), 400

        # Get the employee who made the leave request
        employee = User.query.get(leave_request.employee_id)
        
        # Update approval fields (first stage)
        leave_request.status = 'approved' if action == 'approve' else 'rejected'
        leave_request.approved_by = current_user.id
        leave_request.approved_at = datetime.utcnow()
        leave_request.action_comment = data.get('action_comment', '')

        # If rejected at approval stage, calculate current remaining days (no deduction)
        if action == 'reject':
            current_remaining = (float(employee.total_no_leave_days_annual or 0) - 
                               sum(float(leave.days) for leave in 
                                   LeaveRequest.query.filter_by(employee_id=employee.id, status='authorised').all()))
            leave_request.no_of_leave_days_remaining = current_remaining

        # Don't calculate leave days for approvals yet - that happens at authorization stage
        
        db.session.commit()
        return jsonify(leave_request.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/<int:request_id>/authorise', methods=['POST'])
@jwt_required()
@manager_required
def authorise_leave_request(request_id):
    """HR/Manager authorises an approved leave request (second stage)."""
    try:
        current_user = get_current_user()
        leave_request = LeaveRequest.query.get(request_id)
        if not leave_request:
            return jsonify({'error': 'Leave request not found'}), 404

        if leave_request.status != 'approved':
            return jsonify({'error': 'Leave request must be approved first'}), 400

        data = request.get_json()
        action = data.get('action')  # 'authorise' or 'reject'

        if action not in ['authorise', 'reject']:
            return jsonify({'error': 'Invalid action. Must be "authorise" or "reject"'}), 400

        # Get the employee who made the leave request
        employee = User.query.get(leave_request.employee_id)
        
        # Update authorization fields (second stage)
        if action == 'authorise':
            leave_request.status = 'authorised'
            leave_request.authorised_by = current_user.id
            leave_request.authorised_at = datetime.utcnow()
            
            # NOW calculate and update remaining leave days (only on authorization)
            authorised_leaves = LeaveRequest.query.filter_by(
                employee_id=employee.id, 
                status='authorised'
            ).all()
            
            total_used_days = sum(float(leave.days) for leave in authorised_leaves) + float(leave_request.days)
            annual_allocation = float(employee.total_no_leave_days_annual or 0)
            remaining_days = annual_allocation - total_used_days
            
            # Update both the leave request and user records
            leave_request.no_of_leave_days_remaining = remaining_days
            employee.total_no_leave_days_annual_float = remaining_days
            
            # Find the "On Leave" shift and create roster entries
            leave_shift = Shift.query.filter_by(name='On Leave').first()
            if leave_shift:
                current_date = leave_request.start_date
                while current_date <= leave_request.end_date:
                    # Check if a shift already exists for this employee on this day
                    existing_roster = ShiftRoster.query.filter_by(
                        employee_id=leave_request.employee_id,
                        date=current_date
                    ).first()

                    if not existing_roster:
                        new_roster_entry = ShiftRoster(
                            employee_id=leave_request.employee_id,
                            shift_id=leave_shift.id,
                            date=current_date,
                            hours=0,
                            status='approved'
                        )
                        db.session.add(new_roster_entry)

                    current_date += timedelta(days=1)
        else:
            # Rejected at authorization stage - revert to pending or rejected
            leave_request.status = 'rejected'
            leave_request.authorised_by = current_user.id
            leave_request.authorised_at = datetime.utcnow()
            
            # No change to remaining days since it was never deducted
            current_remaining = (float(employee.total_no_leave_days_annual or 0) - 
                               sum(float(leave.days) for leave in 
                                   LeaveRequest.query.filter_by(employee_id=employee.id, status='authorised').all()))
            leave_request.no_of_leave_days_remaining = current_remaining

        # Add authorization comment if provided
        auth_comment = data.get('action_comment', '')
        if auth_comment:
            existing_comment = leave_request.action_comment or ''
            leave_request.action_comment = f"{existing_comment}\nAuth: {auth_comment}" if existing_comment else f"Auth: {auth_comment}"

        db.session.commit()
        return jsonify(leave_request.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Keep the old endpoint for backward compatibility (deprecated)
@leave_bp.route('/<int:request_id>/action', methods=['POST'])
@jwt_required()
@manager_required
def action_leave_request(request_id):
    """Legacy endpoint - redirects to approve endpoint."""
    return approve_leave_request(request_id)

@leave_bp.route('/<int:request_id>', methods=['DELETE'])
@jwt_required()
def delete_leave_request(request_id):
    """Delete a pending leave request."""
    try:
        current_user = get_current_user()
        leave_request = LeaveRequest.query.get(request_id)

        if not leave_request:
            return jsonify({'error': 'Leave request not found'}), 404

        # Check if the user is the owner and the request is still pending
        if leave_request.employee_id != current_user.id:
            return jsonify({'error': 'You can only delete your own leave requests'}), 403

        if leave_request.status != 'pending':
            return jsonify({'error': 'Cannot delete a request that has already been processed'}), 400

        db.session.delete(leave_request)
        db.session.commit()

        return jsonify({'message': 'Leave request deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/<int:request_id>/attachment', methods=['GET'])
@jwt_required()
def download_attachment(request_id):
    """Download the attachment for a leave request."""
    try:
        current_user = get_current_user()
        leave_request = LeaveRequest.query.get(request_id)
        
        if not leave_request:
            return jsonify({'error': 'Leave request not found'}), 404
        
        # Check permissions - employee can view their own, managers can view all
        if (leave_request.employee_id != current_user.id and 
            current_user.role_ref.name not in ['Admin', 'Manager']):
            return jsonify({'error': 'Not authorized to view this attachment'}), 403
        
        if not leave_request.attachment_filename:
            return jsonify({'error': 'No attachment found for this leave request'}), 404
        
        # Check if file exists
        if not os.path.exists(leave_request.attachment_path):
            return jsonify({'error': 'Attachment file not found on server'}), 404
        
        # Get file stats for caching
        file_stat = os.stat(leave_request.attachment_path)
        file_mtime = file_stat.st_mtime
        file_size = file_stat.st_size
        
        # Create ETag based on file path, size, and modification time
        etag_data = f"{leave_request.attachment_path}-{file_size}-{file_mtime}"
        etag = hashlib.md5(etag_data.encode()).hexdigest()
        
        # Check if client has cached version
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match == etag:
            # Client has the current version, return 304 Not Modified
            response = jsonify()
            response.status_code = 304
            response.headers['ETag'] = etag
            response.headers['Cache-Control'] = 'public, max-age=3600'  # 1 hour
            return response

        # Return file with caching headers
        response = send_file(
            leave_request.attachment_path,
            as_attachment=False,  # Changed to False for viewing, True for download
            download_name=leave_request.attachment_filename,
            mimetype=leave_request.attachment_mimetype
        )
        
        # Add caching headers
        response.headers['ETag'] = etag
        response.headers['Cache-Control'] = 'public, max-age=3600'  # 1 hour
        response.headers['Last-Modified'] = datetime.fromtimestamp(file_mtime).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/<int:request_id>/attachment/download', methods=['GET'])
@jwt_required()
def download_attachment_file(request_id):
    """Download the attachment file (force download)."""
    try:
        current_user = get_current_user()
        leave_request = LeaveRequest.query.get(request_id)
        
        if not leave_request:
            return jsonify({'error': 'Leave request not found'}), 404
        
        # Check permissions
        if (leave_request.employee_id != current_user.id and 
            current_user.role_ref.name not in ['Admin', 'Manager']):
            return jsonify({'error': 'Not authorized to download this attachment'}), 403
        
        if not leave_request.attachment_filename:
            return jsonify({'error': 'No attachment found for this leave request'}), 404
        
        # Check if file exists
        if not os.path.exists(leave_request.attachment_path):
            return jsonify({'error': 'Attachment file not found on server'}), 404
        
        # Force download
        return send_file(
            leave_request.attachment_path,
            as_attachment=True,  # Force download
            download_name=leave_request.attachment_filename,
            mimetype=leave_request.attachment_mimetype
        )
    except Exception as e:
        print(f"Error downloading attachment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/<int:request_id>/attachment', methods=['POST'])
@jwt_required()
def upload_attachment(request_id):
    """Upload an attachment to an existing leave request."""
    try:
        current_user = get_current_user()
        leave_request = LeaveRequest.query.get(request_id)
        
        if not leave_request:
            return jsonify({'error': 'Leave request not found'}), 404
        
        # Check permissions - only the employee who created the request can add attachments
        # and only if the request is still pending
        if leave_request.employee_id != current_user.id:
            return jsonify({'error': 'Not authorized to modify this leave request'}), 403
        
        if leave_request.status != 'pending':
            return jsonify({'error': 'Cannot add attachments to processed leave requests'}), 400
        
        file = request.files.get('attachment')
        if not file or file.filename == '':
            return jsonify({'error': 'No file provided'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File size exceeds 5MB limit'}), 400
        
        try:
            # Remove old attachment if exists
            if leave_request.attachment_path and os.path.exists(leave_request.attachment_path):
                os.remove(leave_request.attachment_path)
            
            # Save new attachment
            file_info = save_leave_attachment(file, leave_request.id)
            
            # Update leave request with new file info
            leave_request.attachment_filename = file_info['filename']
            leave_request.attachment_path = file_info['path']
            leave_request.attachment_mimetype = file_info['mimetype']
            leave_request.attachment_size = file_info['size']
            leave_request.attachment_uploaded_at = datetime.utcnow()
            
            db.session.commit()
            return jsonify(leave_request.to_dict()), 200
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'File upload failed: {str(e)}'}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/<int:request_id>/attachment', methods=['DELETE'])
@jwt_required()
def delete_attachment(request_id):
    """Delete the attachment from a leave request."""
    try:
        current_user = get_current_user()
        leave_request = LeaveRequest.query.get(request_id)
        
        if not leave_request:
            return jsonify({'error': 'Leave request not found'}), 404
        
        # Check permissions - only the employee who created the request can delete attachments
        # and only if the request is still pending
        if leave_request.employee_id != current_user.id:
            return jsonify({'error': 'Not authorized to modify this leave request'}), 403
        
        if leave_request.status != 'pending':
            return jsonify({'error': 'Cannot remove attachments from processed leave requests'}), 400
        
        if not leave_request.attachment_filename:
            return jsonify({'error': 'No attachment found for this leave request'}), 404
        
        # Remove file from filesystem
        if leave_request.attachment_path and os.path.exists(leave_request.attachment_path):
            os.remove(leave_request.attachment_path)
        
        # Clear attachment fields
        leave_request.attachment_filename = None
        leave_request.attachment_path = None
        leave_request.attachment_mimetype = None
        leave_request.attachment_size = None
        leave_request.attachment_uploaded_at = None
        
        db.session.commit()
        return jsonify({'message': 'Attachment deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

